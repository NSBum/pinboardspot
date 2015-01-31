## pinboardspot ##

Make your Pinboard bookmarks Spotlight searchable.

I use Pinboard almost exclusively to bookmark interesting places on the web because it allows me to attach metadata to them that Safari can't. But, Pinboard bookmarks aren't Spotlight-searchable. This Python application allows you to keep a local copy of your Pinboard bookmarks complete with tags that are applied to local `.webloc` files.

## Usage ##

1. __Install `tag`__

    The Python script makes use of a command line application to apply OS X tags to the local bookmarks. You will need to install [`tag`](https://github.com/jdberry/tag to use this script. I would install it using [Homebrew](http://brew.sh): `brew install tag`.

2. __Calling the script__

    You will need to supply at least the following arguments:

    - `-u, --user`		Your Pinboard user name
    - `-p, --password`	Your Pinboard password
    - `-w, --webloc`		The path on your filesystem where the webloc files will be stored

    Optionally, you can specify the path to the sqlite3 database that the script uses.

    `-d, --database`	The path on your filesystem where the sqlite3 database is stored

