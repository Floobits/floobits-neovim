# [Floobits](https://floobits.com/) NeoVim Plugin

[![Floobits Status](https://floobits.com/Floobits/nvim-plugin.svg)](https://floobits.com/Floobits/nvim-plugin/redirect)

Real-time collaborative editing. Think Etherpad, but with native editors. This is the plugin for [NeoVim](https://github.com/neovim/neovim) which replaces our [Vim plugin](https://github.com/Floobits/floobits-vim). We also have plugins for [Emacs](https://github.com/Floobits/floobits-emacs), [Sublime Text](https://github.com/Floobits/floobits-sublime), and [IntelliJ](https://github.com/Floobits/floobits-intellij), as well as a web-based editor that supports video chat and screen sharing.

### Development status: fairly stable, should work.

## Installation

Install the plugin in one of the ways described below and then run `:UpdateRemotePlugins` in Neovim. For the next step please restart neovim. You will need to rerun this command whenever there are updates for the Floobits plugin. Please see `:he remote-plugin` for more information.

### Python

Python is required, please see `he: nvim-python` for instructions.

### Vundle

*Recommended*

Using Vundle, add this to your Vundle section in `~/.config/nvim/init.vim`:

```
Plugin 'floobits/floobits-neovim'
```

Consult the [Vundle Readme](https://github.com/gmarik/Vundle.vim/blob/master/README.md) for how to set up Vundle.

**Please make sure your Vundle is up to date!**


### Manual (*Not recommended*)

Clone:

```
cd ~/.config/nvim/rplugin
git clone https://github.com/Floobits/floobits-neovim.git
```



Move or symlink the rplugin/python directory contents and plugin directories into your `~/.nvim` directory. You will not get updates this way. You should use vundle. You could symlink these files but then if we add new files or directories you would have problems.


## Setting up the plugin


* [Create a Floobits account](https://floobits.com/signup) or [sign in with GitHub](https://floobits.com/login/github?next=/dash).
* Add your Floobits username and API secret to `~/.floorc.json`. You can find your API secret on [your settings page](https://floobits.com/dash/settings). A typical `~/.floorc.json` looks like this:

```
{
  "auth": {
    "floobits.com": {
      "username": "your_username",
      "api_key": "your_api_key",
      "secret": "your_api_secret_not_your_password"
    }
  }
}
```


## Usage

* `:FlooShareDirPublic /path/to/files`. Share a directory with others. This will create a new workspace, populate it with the files in that directory, and open the workspace's settings in your browser.
* `:FlooShareDirPrivate /path/to/files`. Share a directory with others. This will create a new workspace, populate it with the files in that directory, and open the workspace's settings in your browser.
* `:FlooJoinWorkspace https://floobits.com/owner/workspace_name`. Join a Floobits workspace. Workspace URLs are the same as what you see in the web editor.
* `:FlooLeaveWorkspace`. Leave the workspace.
* `:FlooToggleFollowMode`. Toggle follow mode. Follow mode will follow the most recent changes to buffers.
* `:FlooSummon`. Make everyone in the workspace jump to your cursor.
* `:FlooDeleteBuf`. Delete the current buffer from the workspace.
* `:FlooAddBuf`. Add a buffer to the workspace. If no buffer is specified, the current buffer is used.
* `:FlooRefreshWorkspace`. Scan local workspace copy for changes and prompt to overwrite local/remote if files differ. Useful after switching branches in git.

Typical workflow goes something like this:

1. Either create a workspace or join one (`:FlooShareDir...` or `:FlooJoinWorkspace`)

2. If you're joining and your local files differ from the workspace, you'll be asked which copy you want to keep.

3. As you pair, occasionally you'll want to show your colleague some code in another file. Use `FlooSummon` for this.

4. Unfortunately, neither Vim nor Neovim has hooks for when new files are created. You'll have to add new files to the workspace manually, either by saving them (`:w`) or with `:FlooAddBuf`.

5. When you're done pairing, you can leave the workspace with `:FlooLeaveWorkspace` or by quitting your editor.


## Troubleshooting

If you experience problems, try disabling other plugins before [submitting a bug report](https://github.com/Floobits/floobits-neovim/issues). You can also [get a hold of us using IRC, Twitter, or e-mail](https://floobits.com/help#support).

## Removing the plugin

After removing the plugin from vundle you must again call `:UpdateRemotePlugins`. The plugin may generate the following files and directories:

```
~/.floorc.json
~/floobits
```

You may wish to delete these after removing this plugin.
