#!/usr/bin/env python3

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# Contributor(s): Campbell Barton
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

"""
This script is a utility to Batch process images
using Blender's compositor.

It handles setting the input/output paths and
matching the render resolution to the input.

Example use:

   batch_compo.py --blend=compo.blend --input="./images_src/*.png" --output="./images_dst"
"""


def compo_apply(file_src, file_dst, is_refresh=False):
    """
    Given an input & output, load the file and
    render the output at the same resolution.
    """

    def node_tree_find_input(ntree):
        """
        Gets the input node and returns it.
        First check for the selected, in case there are multiple.
        """
        for is_select in (True, False):
            for node in ntree.nodes:
                if (is_select is False) or node.select:
                    if node.type == 'IMAGE':
                        return node

    def is_path_newer(f_src, f_dst, default=False):
        """
        Is f_src newer than f_dst.
        """
        import os
        try:
            t_src = os.path.getmtime(f_src)
        except:
            return default
        try:
            t_dst = os.path.getmtime(f_dst)
        except:
            return default
        return (t_src > t_dst)

    if is_refresh:
        if not is_path_newer(file_src, file_dst):
            print(" Refresh: skipping up to date: %r" % file_dst)
            return

    print(" Converting %r --> %r" % (file_src, file_dst))

    import bpy
    scene = bpy.context.scene
    render = scene.render
    ntree = scene.node_tree

    node = node_tree_find_input(ntree)
    if node is None:
        print("No Image node found %r" % file_src)
        return

    image = bpy.data.images.load(file_src)
    node.image = image

    # check if the image is loaded
    x, y = image.size

    if x == 0:
        print("Image could not load %r" % file_src)

    render.resolution_x = x
    render.resolution_y = y

    render.resolution_percentage = 100
    render.use_file_extension = False
    render.filepath = file_dst

    bpy.ops.render.render(write_still=True)


def create_argparse():
    import os
    import argparse

    if is_blender:
        usage_text = (
            "Run blender in background mode with this script:"
            "  blender --background "
            "--python " + os.path.basename(__file__) + " -- [options]")
    else:
        usage_text = (
            "Run this script to convert image(s):" +
            os.path.basename(__file__) + " --blend=FILE "
            "--input=FILE --output=FILE [options]")

    parser = argparse.ArgumentParser(description=usage_text)

    # for main_render() only, but validate args.
    parser.add_argument(
            "-i", "--input", dest="path_src", metavar='FILE', required=True,
            help="Input path(s) or a wildcard to glob many files")
    parser.add_argument(
            "-o", "--output", dest="path_dst", metavar='FILE', required=True,
            help="Output file or a directory when multiple inputs are passed")
    parser.add_argument(
            "-r", "--refresh", dest="is_refresh", default=False, action="store_true",
            help="Refresh, only overwrite output if input is newer.")

    # for main_launch() only
    parser.add_argument(
            "-b", "--blend", dest="blend_file", metavar='FILE', required=True,
            help="Blend file to load as a compositor template")
    parser.add_argument(
            "-e", "--bin", dest="blend_bin", metavar='FILE',
            help="Path to the blender binary (use if 'blender' isn't available)")

    return parser


def main_render():
    import sys
    import os

    argv = sys.argv

    if "--" not in argv:
        argv = []  # as if no args are passed
    else:
        argv = argv[argv.index("--") + 1:]  # get all args after "--"

    parser = create_argparse()
    args = parser.parse_args(argv)

    if not argv:
        parser.print_help()
        return

    file_src = args.path_src
    file_dst = args.path_dst

    if os.path.exists(file_src):
        # Single source file
        if os.path.isdir(file_src):
            print("Error: input can't be a directory, "
                  "must be a file or glob all files!")
            sys.exit(1)

        if os.path.isdir(file_dst):
            file_dst = os.path.join(file_dst, os.path.basename(file_src))

        compo_apply(file_src, file_dst, is_refresh=args.is_refresh)
    else:
        # Multiple source files (glob)
        import glob
        file_src_glob = glob.glob(file_src)
        if not file_src_glob:
            print("Warning: input expression doesn't match any files!")
            sys.exit(1)

        if not os.path.exists(file_dst):
            os.makedirs(file_dst)

        if not os.path.isdir(file_dst):
            print("Error: output path must be a directory "
                  "when multiple inputs are given!")
            sys.exit(1)

        for fn_src in file_src_glob:
            if os.path.isdir(fn_src):
                print(" ... Skipping directory %r" % fn_src_abs)
                continue

            fn_dst = os.path.join(file_dst, os.path.basename(fn_src))

            compo_apply(fn_src, fn_dst, is_refresh=args.is_refresh)

    print("batch job finished, exiting")


def main_launch():
    import sys
    import argparse

    argv = sys.argv[1:]

    parser = create_argparse()
    args = parser.parse_args(argv)

    if not argv:
        parser.print_help()
        sys.exit(1)

    cmd = [
        "blender" if not args.blend_bin else args.blend_bin,
        "--background",
        "-noaudio",
        "--factory-startup",
        args.blend_file,
        "--python", __file__,
        "--",
        ] + argv

    import subprocess
    exitcode = subprocess.call(cmd)
    sys.exit(exitcode)


if __name__ == "__main__":
    # support running in/outside of Blender
    try:
        import bpy
        is_blender = True
    except ImportError:
        is_blender = False

    if is_blender:
        main_render()
    else:
        main_launch()
