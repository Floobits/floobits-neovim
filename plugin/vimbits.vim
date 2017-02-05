" Copyright 2014-2017 Floobits, Inc


if !has('python')
   echomsg "Floobits error: no neovim python module. Run `pip install neovim` to fix. For more info, :he nvim-python"
endif


if !exists("floo_log_level")
    let floo_log_level = "msg"
endif
if !exists("floo_delete_local_files")
    let floo_delete_local_files = 1
endif
if !exists("floo_show_highlights")
    let floo_show_highlights = 1
endif
if !exists("floo_sparse_mode")
    let floo_sparse_mode = 0
endif
if !exists("floo_connected")
    let g:floo_connected = 0
endif

function! g:FloobitsGetSelection()
    let m = tolower(mode())
    try
        if 'v' == m
            let pos = getpos("v")
            let line = pos[1]
            let col = pos[2]
            let start = line2byte(line) + col - 2
            let pos = getpos(".")
            let line = pos[1]
            let col = pos[2]
            let end = line2byte(line) + col - 2
            return [[start, end]]
        else
            let pos = line2byte(line(".")) + col(".") - 2
            return [[pos, pos]]
        endif
    catch a:exception
        return [[0, 0]]
    endtry
endfunction
