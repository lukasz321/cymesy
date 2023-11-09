#!/bin/sh

func split_on_delim(string, delimiter, pos)
{
    # Needs a little more hacking if it isnt the last position...
    result=$( echo $string | sed "s/${delim}/\n/g" | tail -n ${pos} )
}
