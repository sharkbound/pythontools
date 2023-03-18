set nocompatible            " disable compatibility to old-time vi
set showmatch               " show matching 
set ignorecase              " case insensitive 
set mouse=v                 " middle-click paste with 
set hlsearch                " highlight search 
set incsearch               " incremental search
set tabstop=4               " number of columns occupied by a tab 
set softtabstop=4           " see multiple spaces as tabstops so <BS> does the right thing
set expandtab               " converts tabs to white space
set shiftwidth=4            " width for autoindents
set autoindent              " indent a new line the same amount as the line just typed
set nu rnu                " relative line numbers hybrid
set wildmode=longest,list   " get bash-like tab completions
" set cc=80                  " set an 80 column border for good coding style
filetype plugin indent on   "allow auto-indenting depending on file type
syntax on                   " syntax highlighting
set mouse=a                 " enable mouse click
" set clipboard=unnamedplus   " using system clipboard
filetype plugin on
" set cursorline              " highlight current cursorline
set ttyfast                 " Speed up scrolling in Vim
" set spell                 " enable spell check (may need to download language package)
" set noswapfile            " disable creating swap file
" set backupdir=~/.cache/vim " Directory to store backup files.

" highlight the visual selection after pressing enter.
xnoremap <silent> <cr> "*y:silent! let searchTerm = '\V'.substitute(escape(@*, '\/'), "\n", '\\n', "g") <bar> let @/ = searchTerm <bar> echo '/'.@/ <bar> call histadd("search", searchTerm) <bar> set hls<cr>

" vim visual multi
" https://github.com/mg979/vim-visual-multi
let g:VM_mouse_mappings = 1

" keymaps for vim-visual-multi mouse actions
nmap   <C-LeftMouse>         <Plug>(VM-Mouse-Cursor)
nmap   <C-RightMouse>        <Plug>(VM-Mouse-Word)  
nmap   <M-C-RightMouse>      <Plug>(VM-Mouse-Column)

" select all occurences in of that selection
nmap <C-e> <Plug>(VM-Select-All)
imap <C-e> <ESC><Plug>(VM-Select-All)
vmap <C-e> <ESC><Plug>(VM-Select-All)


" maps the key <leader> represents, need to be mapped before uses of it
let mapleader=" "

" easy motion search
map z/ <Plug>(incsearch-easymotion-/)
map z? <Plug>(incsearch-easymotion-?)
map zg/ <Plug>(incsearch-easymotion-stay)
map <leader>k <Plug>(easymotion-s)
map <leader>j <Plug>(easymotion-f)

" nerd tree mappings
nnoremap <leader>n :NERDTreeFocus<CR>
nnoremap <C-n> :NERDTree<CR>
nnoremap <C-t> :NERDTreeToggle<CR>
nnoremap <C-f> :NERDTreeFind<CR>

" quick paste/copy to clipboard mappings
map <leader>p "+p<ESC>
map <leader>y "+y<ESC>

" allows incsearch highlighting for range commands
cnoremap $t <CR>:t''<CR>
cnoremap $T <CR>:T''<CR>
cnoremap $m <CR>:m''<CR>
cnoremap $M <CR>:M''<CR>
cnoremap $d <CR>:d<CR>``

" tab movement CTRL+LEFT/RIGHT
nnoremap <C-h> :tabprevious<CR>
nnoremap <C-l> :tabnext<CR>

" make O and o create a new line only, and not go insert mode after
nnoremap oo o<Esc>
nnoremap OO O<Esc>

" Go to tab by number
noremap <leader>1 1gt
noremap <leader>2 2gt
noremap <leader>3 3gt
noremap <leader>4 4gt
noremap <leader>5 5gt
noremap <leader>6 6gt
noremap <leader>7 7gt
noremap <leader>8 8gt
noremap <leader>9 9gt

" Use ctrl-[hjkl] to select the active split!
nmap <silent> <c-k> :wincmd k<CR>
nmap <silent> <c-j> :wincmd j<CR>
nmap <silent> <c-h> :wincmd h<CR>
nmap <silent> <c-l> :wincmd l<CR>

call plug#begin('~/AppData/Local/nvim/autoload/plugged')
" Plugin Section
 Plug 'dracula/vim'
 Plug 'ryanoasis/vim-devicons'
 " Plug 'SirVer/ultisnips'
 Plug 'honza/vim-snippets'
 Plug 'scrooloose/nerdtree'
 Plug 'preservim/nerdcommenter'
 Plug 'mhinz/vim-startify'
 Plug 'tpope/vim-surround'
 Plug 'easymotion/vim-easymotion'
 Plug 'tpope/vim-repeat'
 Plug 'machakann/vim-highlightedyank'  
 Plug 'haya14busa/incsearch-easymotion.vim'
 Plug 'haya14busa/incsearch.vim'
 Plug 'mg979/vim-visual-multi', {'branch': 'master'}
 Plug 'junegunn/fzf', { 'do': { -> fzf#install() } }
 Plug 'junegunn/fzf.vim' 
 Plug 'ggreer/the_silver_searcher'
 Plug 'nvim-lua/plenary.nvim' " don't forget to add this one if you don't have it yet!
 Plug 'ThePrimeagen/harpoon'
" Plug 'nvim-treesitter/nvim-treesitter'
" Plug 'LeonGr/neovim-expand-selection'
call plug#end()
