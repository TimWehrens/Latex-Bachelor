#!/usr/bin/env perl
$latex = 'lualatex -interaction=nonstopmode -shell-escape';
$bibtex = 'biber %B';
$makeindex = 'makeindex %O -o %D %S';
$max_repeat = 5;
