#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import re

def parse_return_type(return_type):
    result_prefix = "std::result::Result<"
    result_prefix_len = len(result_prefix)
    option_prefix = "std::option::Option<"
    option_prefix_len = len(option_prefix)
    if return_type.startswith(result_prefix):
        blank_pos = return_type[result_prefix_len:].find(' ')
        if blank_pos != -1:
            return return_type[result_prefix_len:result_prefix_len+blank_pos-1]
        else:
            print("ERR:", return_type, file=sys.stderr)
            assert False
    elif return_type.startswith(option_prefix):
        greater_pos = return_type[:option_prefix_len:-1].find('>')  # reverse find
        if greater_pos != -1:
            return return_type[option_prefix_len:-(greater_pos+1)]
        else:
            print("ERR:", return_type, file=sys.stderr)
            assert False
    else:
        return return_type
    

def parse_fn(is_ref, line):
    self_type = ""
    self_pos = line.find("_1: ")
    if (self_pos != -1):
        self_pos += len("_1: ")
        next_arg_pos = line[self_pos:].find(", _2: ")
        if next_arg_pos != -1:
            self_type = line[self_pos:self_pos+next_arg_pos]
        else:
            bracket_pos = line[self_pos:].find(")")
            if bracket_pos != -1:
                self_type = line[self_pos:self_pos+bracket_pos]

    return_type = ""
    return_pos = line.find("-> ")
    if (return_pos != -1):
        return_pos += len("-> ")
        end_pos = line[return_pos:].find("{")
        if end_pos != -1:
            end_pos -= 1
            return_type = parse_return_type(line[return_pos:return_pos + end_pos])
    return self_type, return_type

def search_mir(infile):
    # fn  <impl at src/main.rs:9:1: 25:2>::peek2(_1: &S) -> std::result::Result<&P, ()>
    pattern_ref = re.compile(r"fn\s.+<impl .+>::.+\(_1: &.+\) -> (std::result::Result<&.+, .+>|std::option::Option<&.+>|&.+) {")
    pattern_obj = re.compile(r"fn\s.+<impl .+>::.+\(_1: &.+\) -> (std::result::Result<[^&]+, .+>|std::option::Option<[^&]+>|[^&]+) {")
    results = {}
    for line in infile.readlines():
        if pattern_ref.match(line):
            # print("REF: {}".format(line), end="")
            self_type, return_type = parse_fn(True, line)
            # print(self_type, return_type)
            if return_type == "" or return_type == "()" or return_type == self_type:
                continue
            if self_type not in results:
                results[self_type] = {("R", return_type, line)}
            else:
                results[self_type].add(("R", return_type, line))
        elif pattern_obj.match(line):
            # print("OBJ: {}".format(line), end="")
            self_type, return_type = parse_fn(False, line)
            # print(self_type, return_type)
            if return_type == "" or return_type == "()" or "Result<()" in return_type or return_type == self_type[1:]:  # remove & from self_type
                continue
            if self_type not in results:
                results[self_type] = {("O", return_type, line)}
            else:
                results[self_type].add(("O", return_type, line))

    for self_type, value in results.items():
        # print(self_type, value)
        return_type_map = {}
        for x in value:
            if x[0] == "O":
                if x[1] not in return_type_map:
                    return_type_map[x[1]] = set()
                return_type_map[x[1]].add(("O", x[2]))
            elif x[0] == "R":
                if "&mut " in x[1]:
                    return_type = x[1][len("&mut "):]
                else:
                    return_type = x[1][1:]  # transform to obj
                if return_type not in return_type_map:
                    return_type_map[return_type] = set()
                return_type_map[return_type].add(("R", x[2]))
    
        for return_obj, ref_lines in return_type_map.items():
            return_obj = False
            return_ref = False
            for v in ref_lines:
                ref, line = v[0], v[1]
                if not return_obj and ref == "O":
                    return_obj = True
                elif not return_ref and ref == "R":
                    return_ref = True
                if return_obj and return_ref:
                    break
            if return_obj and return_ref:
                print("SELF TYPE:", self_type)
                for v in ref_lines:
                    ref, line = v[0], v[1]
                    print("{}, {}".format(ref, line))

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

