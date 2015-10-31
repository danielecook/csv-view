from flask import Flask, render_template, redirect, url_for
from csvdiff import diff_files, patch
import webbrowser
from collections import OrderedDict
from io import StringIO
import csv
from git import Repo
import json
import os
import sys
import random, threading, webbrowser



app = Flask(__name__)
repo = Repo(search_parent_directories=True)

def git_path(filename):
    return os.path.abspath(filename).replace(os.path.split(repo.git_dir)[0], "").strip("/")


def commit_to_csv(commit, csv_filename):
    """
        Get a CSV generator from a git commit.
    """
    repo.git_dir
    data = (commit.tree / csv_filename).data_stream.read()
    dialect = csv.Sniffer().sniff(StringIO(unicode(data)).read(1024))
    data = data.splitlines()
    for n, row in enumerate(data):
        if n == 0:
            data[n] = "ID" + dialect.delimiter + row
        else:    
            data[n] = str(n) + dialect.delimiter + row
    data = "\n".join(data)
    csv_out = csv.DictReader(StringIO(unicode(data), newline=None), dialect=dialect)
    return csv_out


@app.route("/")
def home():
    if len(sys.argv) > 1:
        csv_filename = sys.argv[1]
        return redirect(url_for('first_change', csv_filename = csv_filename))
    else:
        path = os.path.curdir
    files = [x for x in os.listdir(".") if os.path.isfile(x)]
    return render_template("home.html", **locals())

@app.route("/diff/<csv_filename>/")
def first_change(csv_filename):
    csv_filename_rel = os.path.abspath(csv_filename).replace(os.path.split(repo.git_dir)[0], "")
    commits = [x for x in repo.iter_commits(paths=os.path.abspath(csv_filename))]
    commit_new_sha = commits[0].hexsha
    commit_old_sha = commits[1].hexsha
    return redirect(url_for('diff', csv_filename = csv_filename, 
                                    commit_new_sha = commit_new_sha,
                                    commit_old_sha = commit_old_sha))

@app.route("/diff/<commit_old_sha>/<commit_new_sha>/<path:csv_filename>/")
def diff(csv_filename, commit_old_sha = None, commit_new_sha = None):
    csv_filename_rel = git_path(csv_filename)
    commits = [x for x in repo.iter_commits(paths=os.path.abspath(csv_filename))]
    commit_old = repo.commit(commit_old_sha)
    commit_new = repo.commit(commit_new_sha)
    csv_new = commit_to_csv(commit_new, csv_filename_rel)
    fieldnames = csv_new.fieldnames
    out_table = []
    for row in commit_to_csv(commit_new,  csv_filename_rel):
        out_table.append(OrderedDict(row))

    csv_old = commit_to_csv(commit_old,csv_filename_rel)
    print csv_old.fieldnames
    p = patch.create(csv_old, csv_new, ["ID"])

    return render_template("main.html", **locals())

def main():
    app.debug = True
    port = 5000
    url = "http://127.0.0.1:{0}".format(port)
    threading.Timer(1.25, lambda: webbrowser.open(url) ).start()
    app.run()