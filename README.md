# separable_merge

<img src="previews/icon.png" width="200">

This is a file merger and splitter which uses an algorithm designed by me to merge multiple files and split files. This file merging algorithm, which I call it `separable merge`, could merge multiple files into a single binary file, which could be split into the original files later. The splitting information stored as the header of the merged file. This algorithm could store not only files, but also folders into a single binary file. The folders could be nested, and all of the file locations with folders will be stored in the splitting information. The type of file that this algorithm generates could be a merged file standard on its own, I think we can call it `fm`, which stands for `file merge`.

This file merging and splitting algorithm supports all file types, and is cross-platform since its design is based on basic python data structures, it will work fine on all of Windows, Linux and macOS. 

Currently I already implement an file merger and splitter executable which works on Windows, the python script which compiles into the executable should also works on Linux and macOS with python >= 3.7 installed (`pip install tkfilebrowser` is needed for the merger).

There is also a file splitter in this repository, which is simply a program that could cut a file into several parts, you can choose to cut in a number of parts evenly or cut in a fixed file size.

With the file merger and splitter, you can merge any files and folders into a single binary file, and open the merged file to browse the files inside it, with all of the files and folders accessible, you can choose to split selected files and folders in that merged file.

The default file extension of merged file generated by this algorithm is `.fm`, and there is a `file merge task` file which stores current merged task has a default file extension `.fmt`.

On Windows, you can firstly generate a `.fm` file by merging some of the files, and then right click on the merged file to choose `Open with` and then browse and select `file merger.exe` and then choose to always open this type of file using it. Then you can double click on the `.fm` file to open with the file merger and splitter executable, which will shows you the splitpable file list inside the merged file. This is similar for `.fmt` file, which could be imported in the executable when you double click on it after the same steps.

Here is the shortcuts of the file merger and splitter.

![image](previews/1.jpg)

![image](previews/2.jpg)
