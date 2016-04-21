#!/usr/bin/env python
# Copyright 2013, Big Switch Networks, Inc.
#
# LoxiGen is licensed under the Eclipse Public License, version 1.0 (EPL), with
# the following special exception:
#
# LOXI Exception
#
# As a special exception to the terms of the EPL, you may distribute libraries
# generated by LoxiGen (LoxiGen Libraries) under the terms of your choice, provided
# that copyright and licensing notices generated by LoxiGen are not altered or removed
# from the LoxiGen Libraries and the notice provided below is (i) included in
# the LoxiGen Libraries, if distributed in source code form and (ii) included in any
# documentation for the LoxiGen Libraries, if distributed in binary form.
#
# Notice: "Copyright 2013, Big Switch Networks, Inc. This library was generated by the LoxiGen Compiler."
#
# You may not use this file except in compliance with the EPL or LOXI Exception. You may obtain
# a copy of the EPL at:
#
# http://www.eclipse.org/legal/epl-v10.html
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# EPL for the specific language governing permissions and limitations
# under the EPL.

import sys
import os
import unittest

root_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
sys.path.insert(0, root_dir)

import pyparsing
import loxi_front_end.parser as parser

class StructTests(unittest.TestCase):
    def test_empty(self):
        src = """\
struct foo { };
"""
        ast = parser.parse(src)
        self.assertEquals(ast, [['struct', 'foo', [], None, []]])

    def test_one_field(self):
        src = """\
struct foo {
    uint32_t bar;
};
"""
        ast = parser.parse(src)
        self.assertEquals(ast,
            [['struct', 'foo', [], None, [['data', ['scalar', 'uint32_t'], 'bar']]]])

    def test_struct_align_arg(self):
        src = """\
struct foo(align=8) {
    uint32_t bar;
};
"""
        ast = parser.parse(src)
        self.assertEquals(ast,
            [['struct', 'foo', [['align', '8']], None, [['data', ['scalar', 'uint32_t'], 'bar']]]])

    def test_multiple_fields(self):
        src = """\
struct foo {
    uint32_t bar;
    uint8_t baz;
    uint64_t abc;
};
"""
        ast = parser.parse(src)
        self.assertEquals(ast,
            [['struct', 'foo', [], None,
                [['data', ['scalar', 'uint32_t'], 'bar'],
                 ['data', ['scalar', 'uint8_t'], 'baz'],
                 ['data', ['scalar', 'uint64_t'], 'abc']]]])

    def test_array_type(self):
        src = """\
struct foo {
    uint32_t[4] bar;
};
"""
        ast = parser.parse(src)
        self.assertEquals(ast,
            [['struct', 'foo', [], None, [['data', ['array', 'uint32_t[4]'], 'bar']]]])

    def test_list_type(self):
        src = """\
struct foo {
    list(of_action_t) bar;
};
"""
        ast = parser.parse(src)
        self.assertEquals(ast,
            [['struct', 'foo', [], None, [['data', ['list', 'list(of_action_t)'], 'bar']]]])

    def test_pad_member(self):
        src = """\
struct foo {
    pad(1);
};
"""
        ast = parser.parse(src)
        self.assertEquals(ast,
            [['struct', 'foo', [], None, [['pad', 1]]]])

    def test_type_member(self):
        src = """\
struct foo {
    uint16_t foo == 0x10;
};
"""
        ast = parser.parse(src)
        self.assertEquals(ast,
            [['struct', 'foo', [], None, [['type', ['scalar', 'uint16_t'], 'foo', 0x10]]]])

    def test_inheritance(self):
        src = """\
struct foo : bar {
    uint16_t foo == 0x10;
};
"""
        ast = parser.parse(src)
        self.assertEquals(ast,
            [['struct', 'foo', [], 'bar', [['type', ['scalar', 'uint16_t'], 'foo', 0x10]]]])

    def test_discriminator(self):
        src = """\
struct foo {
    uint16_t foo == ?;
};
"""
        ast = parser.parse(src)
        self.assertEquals(ast,
            [['struct', 'foo', [], None, [['discriminator', ['scalar', 'uint16_t'], 'foo']]]])

    def test_field_length(self):
        src = """\
struct foo {
    uint16_t list_len == length(list);
    list(of_uint32_t) list;
};
"""
        ast = parser.parse(src)
        self.assertEquals(ast,
            [['struct', 'foo', [], None, [
                ['field_length', ['scalar', 'uint16_t'], 'list_len', 'list'],
                ['data', ['list', 'list(of_uint32_t)'], 'list']]]])

class EnumTests(unittest.TestCase):
    def test_empty(self):
        src = """\
enum foo {
};
"""
        ast = parser.parse(src)
        self.assertEquals(ast, [['enum', 'foo', [], []]])

    def test_one(self):
        src = """\
enum foo {
    BAR = 1
};
"""
        ast = parser.parse(src)
        self.assertEquals(ast, [['enum', 'foo', [], [['BAR', [], 1]]]])

    def test_params(self):
        src = """\
enum foo(wire_type=uint32, bitmask=False, complete=False) {
    BAR = 1
};
"""
        ast = parser.parse(src)
        self.assertEquals(ast, [['enum', 'foo',
            [ ['wire_type', 'uint32'], ['bitmask','False'], ['complete', 'False']],
            [['BAR', [], 1]]]])

    def test_multiple(self):
        src = """\
enum foo {
    OFP_A = 1,
    OFP_B = 2,
    OFP_C = 3
};
"""
        ast = parser.parse(src)
        self.assertEquals(ast, [['enum', 'foo', [], [['OFP_A', [], 1], ['OFP_B', [], 2], ['OFP_C', [], 3]]]])

    def test_trailing_comma(self):
        src = """\
enum foo {
    OFP_A = 1,
    OFP_B = 2,
    OFP_C = 3,
};
"""
        ast = parser.parse(src)
        self.assertEquals(ast, [['enum', 'foo', [], [['OFP_A', [], 1], ['OFP_B', [], 2], ['OFP_C', [], 3]]]])

class TestMetadata(unittest.TestCase):
    def test_version(self):
        src = """\
#version 1
"""
        ast = parser.parse(src)
        self.assertEquals(ast, [['metadata', 'version', '1']])

class TestToplevel(unittest.TestCase):
    def test_multiple_structs(self):
        src = """\
struct foo { };
struct bar { };
"""
        ast = parser.parse(src)
        self.assertEquals(ast,
            [['struct', 'foo', [], None, []], ['struct', 'bar', [], None, []]])

    def test_comments(self):
        src = """\
// comment 1
struct foo { //comment 2
// comment 3
   uint32_t a; //comment 5
// comment 6
};
// comment 4
"""
        ast = parser.parse(src)
        self.assertEquals(ast,
            [['struct', 'foo', [], None, [['data', ['scalar', 'uint32_t'], 'a']]]])

    def test_mixed(self):
        src = """\
#version 1
struct foo { };
#version 2
struct bar { };
"""
        ast = parser.parse(src)
        self.assertEquals(ast,
            [['metadata', 'version', '1'],
             ['struct', 'foo', [], None, []],
             ['metadata', 'version', '2'],
             ['struct', 'bar', [], None, []]])

class TestErrors(unittest.TestCase):
    def syntax_error(self, src, regex):
        with self.assertRaisesRegexp(pyparsing.ParseSyntaxException, regex):
            parser.parse(src)

    def test_missing_struct_syntax(self):
        self.syntax_error('struct { uint32_t bar; };',
                          'Expected identifier \(at char 7\)')
        self.syntax_error('struct foo uint32_t bar; };',
                          'Expected "{" \(at char 11\)')
        self.syntax_error('struct foo { uint32_t bar; ;',
                          'Expected "}" \(at char 27\)')
        self.syntax_error('struct foo { uint32_t bar; }',
                          'Expected ";" \(at char 28\)')

    def test_invalid_type_name(self):
        self.syntax_error('struct foo { list<of_action_t> bar; }',
                          'Expected "\(" \(at char 17\)')
        self.syntax_error('struct foo { uint32_t[10 bar; }',
                          'Expected "\]" \(at char 24\)')

    def test_invalid_member_syntax(self):
        self.syntax_error('struct foo { bar; }',
                          'Expected identifier \(at char 16\)')
        self.syntax_error('struct foo { uint32_t bar baz; }',
                          'Expected ";" \(at char 26\)')


if __name__ == '__main__':
    unittest.main()
