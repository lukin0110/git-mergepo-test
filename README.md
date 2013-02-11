git-mergepo
===========
Custom git merge driver for PO and MO files.  This merge driver uses the `msgcat` utility from GNU instead if the default merge functionality of git.  Read more: http://www.gnu.org/software/gettext/manual/html_node/msgcat-Invocation.html

It's an installable debian package which installs 2 custom drivers: for PO files and for MO files.  They're not activated by default.

Install the package:
```
sudo dpkg -i git-mergopo.deb
```

To activate the custom merge drivers you'll have to add the following lines to the `.gitattributes` file of the repository:
```
*.po   merge=pofile
*.pot  merge=pofile
*.mo   merge=mofile
```

Nerdy stuff
===========
Build the debian package manually:
```
dpkg --build git-mergepo
```

The MO driver just ignores merge conflicts, since they don't belong in git actually. It uses the latest version of the MO file.

