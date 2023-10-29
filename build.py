#!/usr/bin/python

import os
import subprocess
from os import path
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

from pynt import main, task

AUTHOR = "lgfrbcsgo"
NAME = "Disable Elite Levels"
DESCRIPTION = "Disables the elite levels during battle"

RELEASE_DEPENDENCIES = [
    "https://github.com/lgfrbcsgo/wot-toolkit/releases/download/v0.1.1/lgfrbcsgo.toolkit_0.1.1.wotmod",
]


@task()
def clean():
    subprocess.check_call(["rm", "-rf", "dist"])


@task(clean)
def wotmod():
    # clean dist directory
    subprocess.check_call(["rm", "-rf", "dist/wotmod"])

    res_path = "dist/wotmod/unpacked/res"
    internal_path = "scripts/client"
    source_dst = path.join(res_path, internal_path)

    # make source directory
    subprocess.check_call(["mkdir", "-p", source_dst])

    # copy sources
    subprocess.check_call(["cp", "-r", "src/.", source_dst])

    # compile sources
    subprocess.check_call(["python2.7", "-m", "compileall", internal_path], cwd=res_path)

    unpacked_dst = "dist/wotmod/unpacked"

    # copy license and readme
    subprocess.check_call(["cp", "-r", "LICENSE", unpacked_dst])
    subprocess.check_call(["cp", "-r", "README.md", unpacked_dst])

    # create meta.xml content
    metadata = """
<root>
    <id>{id}</id>
    <version>{version}</version>
    <name>{name}</name>
    <description>{description}</description>
</root>
    """.format(
        id=get_id(), version=get_version(), name=NAME, description=DESCRIPTION
    )

    # write meta.xml
    with open("dist/wotmod/unpacked/meta.xml", "w") as meta_file:
        meta_file.write(metadata.strip())

    # create wotmod file
    wotmod_dst = path.join("dist/wotmod", get_wotmod_name())
    with ZipFile(wotmod_dst, "w", ZIP_STORED) as wotmod_file:
        for file_path in get_files(unpacked_dst):
            zipped_path = path.relpath(file_path, unpacked_dst)
            with open(file_path, "rb") as unzipped_file:
                wotmod_file.writestr(zipped_path, unzipped_file.read())


@task(wotmod)
def release():
    # clean dist directory
    subprocess.check_call(["rm", "-rf", "dist/release"])

    # make release directory
    unpacked_dst = "dist/release/unpacked"
    subprocess.check_call(["mkdir", "-p", unpacked_dst])

    # copy wotmod
    wotmod_dst = path.join("dist/wotmod", get_wotmod_name())
    subprocess.check_call(["cp", wotmod_dst, unpacked_dst])

    # fetch dependencies
    for dependency in RELEASE_DEPENDENCIES:
        subprocess.check_call(["wget", "-nv", "-P", unpacked_dst, dependency])

    # create release archive
    release_dst = path.join("dist/release", get_release_name())
    with ZipFile(release_dst, "w", ZIP_DEFLATED) as release_file:
        for file_path in get_files(unpacked_dst):
            zipped_path = path.relpath(file_path, unpacked_dst)
            with open(file_path, "rb") as unzipped_file:
                release_file.writestr(zipped_path, unzipped_file.read())


@task(release)
def github_actions_release():
    set_github_actions_output("version", get_version())

    wotmod_path = path.join("dist/wotmod", get_wotmod_name())
    set_github_actions_output("wotmod_path", wotmod_path)
    set_github_actions_output("wotmod_name", get_wotmod_name())

    release_path = path.join("dist/release", get_release_name())
    set_github_actions_output("release_path", release_path)
    set_github_actions_output("release_name", get_release_name())


@task(wotmod)
def install(dst):
    for f in os.listdir(dst):
        if f.startswith("{id}_".format(id=get_id())):
            subprocess.check_call(["rm", f], cwd=dst)

    wotmod_dst = path.join("dist/wotmod", get_wotmod_name())
    subprocess.check_call(["cp", wotmod_dst, dst])


def get_id():
    return "{author}.{name}".format(author=AUTHOR, name=NAME.lower().replace(" ", "-"))


def get_version():
    try:
        tag = subprocess.check_output(["git", "describe", "--tags"]).strip()
        return tag.lstrip("v")
    except subprocess.CalledProcessError:
        return "unknown"


def get_wotmod_name():
    return "{id}_{version}.wotmod".format(id=get_id(), version=get_version())


def get_release_name():
    return "{name}-{version}.zip".format(
        name=NAME.lower().replace(" ", "-"), version=get_version()
    )


def get_files(directory):
    for root, _, files in os.walk(directory):
        for file_name in files:
            yield path.join(root, file_name)


def set_github_actions_output(name, value):
    with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
        f.write("{}={}\n".format(name, value))


if __name__ == "__main__":
    main()
