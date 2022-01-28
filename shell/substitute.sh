#!/bin/sh

func substitute_inline(filepath, to_be_substituted, substitution)
{
    sed -i 's/'$to_be_substituted'/'$substitution'/g' $filepath
}
