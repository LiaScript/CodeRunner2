from typing import List
from compiler import ada, c, cobol, dotnet, elixir, ghc, go, java, mono, python, perl, rust, nasm, nim
from compiler.helper import Response2, Problem2, run_command, prefix


def run(cmd: str, working_directory: str, files: List[str]) -> Response2:
    '''Run a compiler'''

    rslt = None

    if cmd.startswith("gcc ") or cmd.startswith("clang ") or cmd.startswith("g++ ") or cmd.startswith("zig "):
        rslt = c.run(cmd, working_directory)

    elif cmd.startswith("v "):
        # will use the v command for compiling
        rslt = c.run(cmd, working_directory)
        problems = []

        # ... but will correct the output
        for p in rslt["problems"]:
            p["row"] -= 1

            problems.append(p)

        rslt["problems"] = problems

    elif cmd.startswith("dotnet "):
        rslt = dotnet.run(cmd, working_directory)

    elif cmd.startswith("ghc "):
        rslt = ghc.run(cmd, working_directory)

    elif cmd.startswith("gnatmake "):
        rslt = ada.run(cmd, working_directory)

    elif cmd.startswith("go "):
        rslt = go.run(cmd, working_directory)

    elif cmd.startswith("javac "):
        rslt = java.run(cmd, working_directory)

    elif cmd.startswith("mcs "):
        rslt = mono.run(cmd, working_directory)

    elif cmd.startswith("elixirc ") or cmd.startswith("mix ") or cmd.startswith("iex ") or cmd.startswith("elixir "):
        rslt = elixir.run(cmd, working_directory)

    elif cmd.startswith("nasm "):
        rslt = nasm.run(cmd, working_directory)

    elif cmd.startswith("nim "):
        rslt = nim.run(cmd, working_directory)

    elif cmd.startswith("perl "):
        rslt = perl.run(cmd, working_directory)

    elif cmd.startswith("python "):
        rslt = python.run(cmd, working_directory)

    elif cmd.startswith("rustc "):
        rslt = rust.run(cmd, working_directory)

    elif cmd.startswith("cobc "):
        rslt = cobol.run(cmd, working_directory)

    elif cmd.startswith("none"):
        rslt = {"ok": True, "message": "", "problems": []}

    else:
        out = run_command(prefix + cmd, working_directory)
        rslt = {"ok": not len(out.stderr) > 0,
                "message": out.stdout + out.stderr,
                "problems": []}

    return {"ok": rslt["ok"],
            "uid": None,
            "message": rslt["message"],
            "problems": formatting(files, rslt["problems"])}


def formatting(files: List[str], problems) -> List[List[Problem2]]:
    '''
    Translate the list of problems into a nested list of Problems,
    where problems within a single file are chunked by their order
    in the files list.
    '''

    if len(problems) == 0:
        return []

    rslt: List[List[Problem2]] = [[]] * len(files)

    index = {}

    for (i, file) in enumerate(files):
        index[file] = i

    for prob in problems:
        if prob["file"]  in index:
            rslt[index[prob["file"]]].append(
                {"type": prob["type"],
                "row": prob["row"],
                "col": prob["col"],
                "text": prob["text"]
            })

    return rslt
