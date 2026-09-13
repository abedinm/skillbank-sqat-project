#!/usr/bin/env python3
"""
make_schedule.py - emit the testing schedule as a GanttProject file.

The assignment brief says: "Schedule must be done using any project management tool.
Don't make the schedule using MS word/excel." So this does not draw a chart. It writes a
real project file that GanttProject (free, ganttproject.biz) or ProjectLibre opens
natively, computes dates and dependencies for, and exports as a Gantt chart.

Workflow:
    1. run this  ->  SkillBank_Test_Schedule.gan
    2. open that file in GanttProject
    3. File > Export > PNG image, save as gantt.png in this folder
    4. re-run make_test_plan.py; it picks gantt.png up as Figure 1 automatically

Task list, durations and dependencies match Table 12 in the plan; both are generated
from the same SCHEDULE constant so they cannot drift apart.
"""

import os
import sys
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_test_plan import SCHEDULE  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "SkillBank_Test_Schedule.gan")
START = "2026-06-01"          # project start; GanttProject rolls dates from here

COLOURS = {
    "Test lead": "#3c7ad9",
    "Test designer": "#8e44ad",
    "Automation engineer": "#16a085",
    "Developer": "#d35400",
    "Test lead, Users": "#c0392b",
    "Developer, Test lead": "#d35400",
}


def main():
    ids = {tid: i + 1 for i, (tid, *_rest) in enumerate(SCHEDULE)}

    tasks = []
    for tid, name, dur, owner, dep in SCHEDULE:
        depends = ""
        if dep and dep != "-":
            for d in [x.strip() for x in dep.split(",")]:
                if d in ids:
                    # type 2 = finish-to-start
                    depends += (f'\n                <depend id="{ids[tid]}" type="2" '
                                f'difference="0" hardness="Strong"/>')
        colour = COLOURS.get(owner, "#8cb6ce")
        # the dependency element belongs to the PREDECESSOR, pointing at the successor
        tasks.append((tid, name, dur, owner, dep, colour))

    # build predecessor -> successors map
    succ = {tid: [] for tid, *_ in SCHEDULE}
    for tid, name, dur, owner, dep in SCHEDULE:
        if dep and dep != "-":
            for d in [x.strip() for x in dep.split(",")]:
                if d in succ:
                    succ[d].append(tid)

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<project name="SkillBank Software Test Plan" company="AIUB - SQAT"'
        f' webLink="" view-date="{START}" view-index="0" gantt-divider-location="380"'
        ' resource-divider-location="300" version="3.2" locale="en_GB">',
        '    <description>Testing schedule for the SkillBank credit-based skill exchange.'
        ' Durations are estimates in working days.</description>',
        '    <view zooming-state="default:3" id="gantt-chart"/>',
        '    <view id="resource-table"/>',
        '    <calendars>',
        '        <day-types>',
        '            <day-type id="0"/>',
        '            <day-type id="1"/>',
        '            <default-week id="1" name="default" sun="1" mon="0" tue="0" wed="0"'
        ' thu="0" fri="0" sat="1"/>',
        '            <only-show-weekends value="false"/>',
        '            <overriden-day-types/>',
        '            <days/>',
        '        </day-types>',
        '    </calendars>',
        '    <tasks empty-milestones="true">',
        '        <taskproperties>',
        '            <taskproperty id="tpd0" name="type" type="default" valuetype="icon"/>',
        '            <taskproperty id="tpd1" name="priority" type="default"'
        ' valuetype="icon"/>',
        '            <taskproperty id="tpd2" name="info" type="default" valuetype="icon"/>',
        '            <taskproperty id="tpd3" name="name" type="default" valuetype="text"/>',
        '            <taskproperty id="tpd4" name="begindate" type="default"'
        ' valuetype="date"/>',
        '            <taskproperty id="tpd5" name="enddate" type="default"'
        ' valuetype="date"/>',
        '            <taskproperty id="tpd6" name="duration" type="default"'
        ' valuetype="int"/>',
        '            <taskproperty id="tpd7" name="completion" type="default"'
        ' valuetype="int"/>',
        '            <taskproperty id="tpd8" name="coordinator" type="default"'
        ' valuetype="text"/>',
        '            <taskproperty id="tpd9" name="predecessorsr" type="default"'
        ' valuetype="text"/>',
        '        </taskproperties>',
    ]

    for tid, name, dur, owner, dep, colour in tasks:
        tnum = ids[tid]
        lines.append(
            f'        <task id="{tnum}" uid="{tid}" name="{escape(tid)} {escape(name)}"'
            f' color="{colour}" meeting="false" start="{START}" duration="{dur}"'
            f' complete="100" thirdDate="{START}" thirdDate-constraint="0" expand="true">')
        lines.append(f'            <notes><![CDATA[Owner: {owner}]]></notes>')
        for s in succ[tid]:
            lines.append(f'            <depend id="{ids[s]}" type="2" difference="0"'
                         f' hardness="Strong"/>')
        lines.append('        </task>')

    lines += [
        '    </tasks>',
        '    <resources>',
    ]
    people = []
    for _, _, _, owner, _ in SCHEDULE:
        for who in [x.strip() for x in owner.split(",")]:
            if who and who not in people:
                people.append(who)
    for i, who in enumerate(people):
        lines.append(f'        <resource id="{i}" name="{escape(who)}" function="Default:0"'
                     f' contacts="" phone=""/>')
    lines += [
        '    </resources>',
        '    <allocations>',
    ]
    for tid, _, _, owner, _ in SCHEDULE:
        for who in [x.strip() for x in owner.split(",")]:
            if who in people:
                lines.append(f'        <allocation task-id="{ids[tid]}"'
                             f' resource-id="{people.index(who)}" function="Default:0"'
                             f' responsible="true" load="100.0"/>')
    lines += [
        '    </allocations>',
        '    <vacations/>',
        '    <taskdisplaycolumns/>',
        '    <roles roleset-name="Default"/>',
        '</project>',
    ]

    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")

    print(f"written: {OUT}  ({os.path.getsize(OUT)/1024:.1f} KB)")
    print(f"  tasks        : {len(SCHEDULE)}")
    print(f"  resources    : {len(people)}  ({', '.join(people)})")
    deps = sum(len(v) for v in succ.values())
    print(f"  dependencies : {deps}")
    print(f"  total effort : {sum(x[2] for x in SCHEDULE)} person-days")
    print()
    print("  next: open this file in GanttProject, then File > Export > PNG")
    print("        save as gantt.png here, and re-run make_test_plan.py")


if __name__ == "__main__":
    main()
