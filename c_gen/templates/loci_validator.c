:: # Copyright 2014, Big Switch Networks, Inc.
:: #
:: # LoxiGen is licensed under the Eclipse Public License, version 1.0 (EPL), with
:: # the following special exception:
:: #
:: # LOXI Exception
:: #
:: # As a special exception to the terms of the EPL, you may distribute libraries
:: # generated by LoxiGen (LoxiGen Libraries) under the terms of your choice, provided
:: # that copyright and licensing notices generated by LoxiGen are not altered or removed
:: # from the LoxiGen Libraries and the notice provided below is (i) included in
:: # the LoxiGen Libraries, if distributed in source code form and (ii) included in any
:: # documentation for the LoxiGen Libraries, if distributed in binary form.
:: #
:: # Notice: "Copyright 2014, Big Switch Networks, Inc. This library was generated by the LoxiGen Compiler."
:: #
:: # You may not use this file except in compliance with the EPL or LOXI Exception. You may obtain
:: # a copy of the EPL at:
:: #
:: # http://www.eclipse.org/legal/epl-v10.html
:: #
:: # Unless required by applicable law or agreed to in writing, software
:: # distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
:: # WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
:: # EPL for the specific language governing permissions and limitations
:: # under the EPL.
::
:: include('_copyright.c')
:: import loxi_globals
:: from loxi_ir import *

/**
 *
 * AUTOMATICALLY GENERATED FILE.  Edits will be lost on regen.
 *
 * Source file for OpenFlow message validation.
 *
 */

#include "loci_log.h"
#include <loci/loci.h>
#include <loci/loci_validator.h>

#define VALIDATOR_LOG(...) LOCI_LOG_ERROR("Validator Error: " __VA_ARGS__)

:: raw_validator_name = lambda cls, version: "loci_validate_%s_%s" % (cls, version.constant_version(prefix='OF_VERSION_'))
:: validator_name = lambda ofclass: "loci_validate_%s_%s" % (ofclass.name, ofclass.protocol.version.constant_version(prefix='OF_VERSION_'))

/* Forward declarations */
:: for version, proto in loxi_globals.ir.items():
:: for ofclass in proto.classes:
static int __attribute__((unused)) ${validator_name(ofclass)}(uint8_t *data, int len, int *out_len);
:: #endfor
:: #endfor

:: readers = { 1: 'buf_u8_get', 2: 'buf_u16_get', 4: 'buf_u32_get' }
:: types = { 1: 'uint8_t', 2: 'uint16_t', 4: 'uint32_t' }

:: for version, proto in loxi_globals.ir.items():

:: # Identify classes in lists and generate list validators
:: seen_lists = set()
:: for ofclass in proto.classes:
:: for m in ofclass.members:
:: if type(m) == OFDataMember and m.oftype.startswith('list'):
:: element_name = m.oftype[8:-3]
:: if element_name in seen_lists:
:: continue
:: #endif
:: seen_lists.add(element_name)
:: list_validator_name = raw_validator_name('of_list_' + element_name, version)
static int __attribute__((unused))
${list_validator_name}(uint8_t *data, int len, int *out_len)
{
    while (len > 0) {
        int cur_len = 0xffff;
        if (${raw_validator_name('of_' + element_name, version)}(data, len, &cur_len) < 0) {
            return -1;
        }
        len -= cur_len;
        data += cur_len;
    }

    return 0;
}

:: #endif
:: #endfor
:: #endfor

:: for ofclass in proto.classes:
static int
${validator_name(ofclass)}(uint8_t *data, int len, int *out_len)
{
    if (len < ${ofclass.base_length}) {
        return -1;
    }

:: if ofclass.is_fixed_length:
    len = ${ofclass.base_length};
:: #endif

:: # Read and validate length fields
:: field_length_members = {}
:: for m in ofclass.members:
:: if type(m) == OFLengthMember:
    ${types[m.length]} wire_len;
    ${readers[m.length]}(data + ${m.offset}, &wire_len);
    if (wire_len > len || wire_len < ${ofclass.base_length}) {
        return -1;
    }

    len = wire_len;

:: elif type(m) == OFFieldLengthMember:
:: # Read field length members
:: field_length_members[m.field_name] = m
    ${types[m.length]} wire_len_${m.field_name};
    ${readers[m.length]}(data + ${m.offset}, &wire_len_${m.field_name});

:: #endif
:: #endfor

:: # Dispatch to subclass validators
:: if ofclass.virtual:
:: discriminator = ofclass.discriminator
    ${types[discriminator.length]} wire_type;
    ${readers[discriminator.length]}(data + ${discriminator.offset}, &wire_type);
    switch (wire_type) {
:: for subclass in proto.classes:
:: if subclass.superclass == ofclass:
    case ${subclass.member_by_name(discriminator.name).value}:
        return ${validator_name(subclass)}(data, len, out_len);
:: #endif
:: #endfor
    }
:: #endif

:: for m in ofclass.members:
:: # Validate field-length members
:: if type(m) == OFDataMember and m.name in field_length_members and m.offset is not None:
    if (${m.offset} + wire_len_${m.name} > len) {
        return -1;
    }

:: #endif
:: if type(m) == OFDataMember and m.oftype.startswith('list') and m.offset is not None:
:: # Validate fixed-offset lists
:: if not m.name in field_length_members:
    int wire_len_${m.name} = len - ${m.offset};
:: #endif
:: element_name = m.oftype[8:-3]
:: list_validator_name = raw_validator_name('of_list_' + element_name, version)
    if (${list_validator_name}(data + ${m.offset}, wire_len_${m.name}, out_len) < 0) {
        return -1;
    }

:: #endif
:: #endfor

:: # TODO handle non-fixed-offset lists

    *out_len = len;
    return 0;
}

:: #endfor
:: #endfor

int
of_validate_message(of_message_t msg, int len)
{
    of_version_t version;
    if (len < OF_MESSAGE_MIN_LENGTH ||
        len != of_message_length_get(msg)) {
        VALIDATOR_LOG("message length %d != %d", len,
                      of_message_length_get(msg));
        return -1;
    }

    version = of_message_version_get(msg);
    int out_len;
    switch (version) {
:: for version, proto in loxi_globals.ir.items():
    case ${version.constant_version(prefix='OF_VERSION_')}:
        return ${validator_name(proto.class_by_name('of_header'))}(msg, len, &out_len);
:: #endfor
    default:
        VALIDATOR_LOG("Bad version %d", OF_VERSION_1_3);
        return -1;
    }
}
