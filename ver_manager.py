#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import getopt
#reload(sys)
import re

#sys.setdefaultencoding('utf-8')

def ver_manager_help():
    sys.stderr.write("Version manager by LLC Svyazcom, Fedorov Alexander\n")
    sys.stderr.write('ver_manager.py -a <action: next_commit>\n')

def get_DSTK_VERSION(version):
    regexpr = re.compile(r'(\d*)\.(\d*)\.(\d*)')
    try:
        ver_major, ver_minor, ver_commit = regexpr.match(version).groups()
        return [int(ver_major), int(ver_minor)]
    except AttributeError:
            sys.stderr.write('Error: ' + line + '\n')
            sys.exit(1)


def main(argv):
    file_name_version = "version.txt"
    action=None
    src_file=None
    in_file=None
    
    try:        
        opts, args = getopt.getopt(argv,"ha:s:i:",["action=","src="])
    except getopt.GetoptError:
        ver_manager_help_help();
        sys.exit(1)
    for opt, arg in opts:
        if opt == '-h':
            ver_manager_help();
            sys.exit(1)
        elif opt == '-a':
            action= arg
        elif opt == '-s':
            src_file= arg
        elif opt == '-i':
            in_file= arg

    version = read_version(file_name_version);
    if version is None:
        print("version file '%s' is incorrect"%(file_name_version))

    if action == "next_commit" or action == "next_minor" or action == "next_major":
        print("Current vestion: ")
        print(version)
        if action == "next_commit":
            version['ver_commit'] += 1
        elif action == "next_minor":
            version['ver_minor'] += 1
            version['ver_commit'] = 0
        elif action == "next_major":
            version['ver_major'] += 1
            version['ver_minor'] = 1
            version['ver_commit'] = 0
        print("New vestion:")
        print(version)
        write_version(file_name_version, version)
    elif action == "modify_py":
        if src_file is not None:
            new_version_text = "version='%d.%d.%d'\n"%(version['ver_major'], version['ver_minor'], version['ver_commit'])
            replace_src(src_file, new_version_text,'python')
            print("file '%s' have been modified"%(src_file))
        else:
            print("src_file isn't defined")
            sys.exit(0)
    elif action == "modify_java":
        if src_file is not None:
            src_text = "\tpublic static final byte[] version = new byte[] { "
            new_version_text = "Version: %d.%d.%d"%(version['ver_major'], version['ver_minor'], version['ver_commit'])            
            chars = list(new_version_text)
            flag_first=1;
            for	char in chars:
                if flag_first == 0:
                    src_text += ", "
                src_text += "'%s'"%(char)
                flag_first=0;
            src_text += "};\n"
            
            src_text += "\tpublic static final byte dstk_ver_major=%d;\n"%(version['ver_major'])
            src_text += "\tpublic static final byte dstk_ver_minor=%d;\n"%(version['ver_minor'])
            
            replace_src(src_file, src_text, 'java')
            print("file '%s' have been modified"%(src_file))
        else:
            print("src_file isn't defined")
            sys.exit(0)
    elif action == "get_version_for_git":
        sys.stdout.write('v%d.%d.%d'%(version['ver_major'], version['ver_minor'], version['ver_commit']))
        sys.exit(0)
    elif action == "replace_stk_part":
        if in_file is not None:
            content = ""
            with open(in_file,"r") as f_in:
                for line in f_in:
                    content += line
            replace_src(src_file, content,'java_stk')
            print("file '%s' have been modified"%(src_file))
        else:
            print("in_file isn't defined")
            sys.exit(0)
    elif action == "replace_parser_part":
        if in_file is not None:
            content = ""
            with open(in_file,"r") as f_in:
                for line in f_in:
                    content += line
            replace_src(src_file, content,'parser')
            print("file '%s' have been modified"%(src_file))
        else:
            print("in_file isn't defined")
            sys.exit(0)
    else:
        ver_manager_help()
    

    

def read_version(file_name):
    pattern = r'\s*(\d*)\.(\d*)\.(\d*)\s*'
    regexpr = re.compile(pattern)
    with open(file_name) as f_in:
        for line in f_in:
            reg_result = regexpr.match(line);
            if reg_result is not None:
                ver_major, ver_minor, ver_commit = reg_result.groups()
                if len(ver_major) > 0 and len(ver_minor) > 0 and len(ver_commit) > 0:
                    return {'ver_major': int(ver_major), 'ver_minor': int(ver_minor), 'ver_commit': int(ver_commit)}
    return None

def write_version(file_name, version):
    with open(file_name,"w") as f_out:
        f_out.write("%d.%d.%d"%(version['ver_major'], version['ver_minor'], version['ver_commit']));
    
    
def replace_src(file_name, replace_string, type_src):
    f_in_lines = []
        ### read
    with open(file_name, "r") as f_in:
        for line in f_in:
#            sys.stdout.write(line)
            f_in_lines.append(line)
            
        ### write
    if type_src=="python":
        r_begin = r'### VERSION_BEGIN'
        r_end = r'### VERSION_END'
    elif type_src=="java_stk":
        r_begin = r'/// STK_PART_BEGIN'
        r_end = r'/// STK_PART_END'
    elif type_src=="parser":
        r_begin = r'/// STK_PARSER_BEGIN'
        r_end = r'/// STK_PARSER_END'
    else:
        r_begin = r'/// VERSION_BEGIN'
        r_end = r'/// VERSION_END'
    with open(file_name,"w") as f_out:
        mode="read"
        for line in f_in_lines:
            if mode == "read":
                f_out.write(line)
            if re.match(r_begin, line):
                mode = "replace"
                f_out.write(replace_string)
            if re.match(r_end, line):
                mode = "read"
                f_out.write(line)                
    

if __name__ == "__main__":
   main(sys.argv[1:])


