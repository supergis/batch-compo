
Batch Compo (Blender)
=====================

This is a simple utility to apply the compositing setup of a ``blend`` file
to an image file (or multiple files).

Motivation
----------

While there are already many batch conversion tools in existence,
not many provide the flexibility of a nodal compositor.


Workflow
--------

- Create a blend file with a compositor setup you want to reuse.
- Ensure there is an image node, which this script can assign the image too.
- Set the output format *(resolution & output path will be overwritten)*.
- Save the file and run ``batch_compo.py`` from the command line.

.. note::

   If there are multiple input images,
   selecting one of them will ensure this is the one
   that gets assigned the input images.


Example Usage
-------------

Converting a single file:

.. code-block:: sh

   batch_compo.py --blend=compo.blend --input="image_src.png" --output="image_dst.png"

Converting a directory full of ``PNG`` images:

.. code-block:: sh

   batch_compo.py --blend=compo.blend --input="./images_src/*.png" --output="./images_dst"


Command Line Args
-----------------

``-b / --blend``
   The ``.blend`` file to use as a template for the batch conversion.

   *Takes a single blend file.*

``-e / --bin`` (optional)
   The Blender executable (use if ``blender`` isn't in the system ``PATH``)

   *Takes a single executable file.*

``-i / --input``
   This takes an input file, which can be any format Blender supports.
   Matching multiple files is also supported, ``images/*.png`` for example.

   *Takes a single file or a glob multiple files.*

   .. note::

      When there are multiple input files,
      the output must be set to a directory.

``-o / --output``

   .. note::

      The output path will be used verbatim,
      the file extensions (such as ``.jpg``, ``.png``) must be included.

   *Takes a single file or directory.*

``-r / --refresh`` (optional)
   When passed, skip converting images when the output files are newer than the input.

   *Takes no arguments*


TODO
----

This script is intentionally kept small/simple,
nevertheless there are some possible additions/improvements.

**match file-format**
   Use the same output format as used by the input format.
**scale-images**
   In the case multiple images are used,
   they could be scaled in the compositor to match the input image.

