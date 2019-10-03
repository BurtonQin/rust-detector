#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import re

def search_mir(infile):
    # fn  <impl at src/main.rs:9:1: 25:2>::peek2(_1: &S) -> std::result::Result<&P, ()>
    pattern_ref = re.compile(r"fn\s.+<impl .+>::.+\(_1: &.+\) -> (std::result::Result<&.+, .+>|std::option::Option<&.+>|&.+) {")
    pattern_obj = re.compile(r"fn\s.+<impl .+>::.+\(_1: &.+\) -> (std::result::Result<[^&]+, .+>|std::option::Option<[^&]+>|[^&]+) {")
    results = {}
    for line in infile.readlines():
        if pattern_ref.match(line):
            print("REF: {}".format(line), end="")
        elif pattern_obj.match(line):
            print("OBJ: {}".format(line), end="")

def test_pattern():
    line1 = """fn  <impl at src/main.rs:9:1: 25:2>::peek2(_1: &S) -> std::result::Result<&P, ()> {"""
    line2 = """fn  <impl at src/main.rs:9:1: 25:2>::peek(_1: &S) -> std::option::Option<&P> {"""
    line3 = """fn  <impl at src/main.rs:9:1: 25:2>::peek(_1: &S) -> &P {"""
    pattern = re.compile(r"fn\s.+<impl .+>::.+\(_1: &.+\) -> (std::result::Result<&.+, .+>|std::option::Option<&.+>|&.+) {")
    
    assert(pattern.match(line1))
    assert(pattern.match(line2))
    assert(pattern.match(line3))
    
    line1 = """fn  <impl at src/main.rs:9:1: 25:2>::peek2(_1: &S) -> std::result::Result<P, ()> {"""
    line2 = """fn  <impl at src/main.rs:9:1: 25:2>::peek(_1: &S) -> std::option::Option<P> {"""
    line3 = """fn  <impl at src/main.rs:9:1: 25:2>::peek(_1: &S) -> P {"""
    pattern = re.compile(r"fn\s.+<impl .+>::.+\(_1: &.+\) -> (std::result::Result<[^&]+, .+>|std::option::Option<[^&]+>|[^&]+) {")

    assert(pattern.match(line1))
    assert(pattern.match(line2))
    assert(pattern.match(line3))

def main():  
    with open(sys.argv[1]) as infile:
        search_mir(infile)

if __name__ == "__main__":
    #test_pattern()
    main()

