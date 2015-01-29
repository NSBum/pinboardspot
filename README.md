## pinboardspot ##

Make your Pinboard bookmarks Spotlight searchable.

I use Pinboard almost exclusively to bookmark interesting places on the web because it allows me to attach metadata to them that Safari can't. But, Pinboard bookmarks aren't Spotlight-searchable. This Python application allows you to keep a local copy of your Pinboard bookmarks complete with tags that are applied to local `.webloc` files.

### Usage ###

The Python script makes use of a command line application to apply OS X tags to the local bookmarks. You will need to install [`tag`](https://github.com/jdberry/tag) to us this script. I would install it using [Homebrew](http://brew.sh): `brew install tag`.