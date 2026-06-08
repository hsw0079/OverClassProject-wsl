# -*- coding: utf-8 -*-
"""
generate_entity_diagram.py
生成实体属性图 .vsdx（基于 Open XML / Visio 2012 格式）
"""
import zipfile
import io
import os
from xml.etree.ElementTree import Element, SubElement, tostring

NS = "http://schemas.microsoft.com/office/visio/2012/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

# ---- 实体定义（硬编码，避免 Django 依赖） ----
ENTITIES = [
    {
        "name": "SchoolVehicle",
        "label": "校内车辆档案",
        "fields": [
            ("plate_number", "Char(20) PK", True),
            ("vehicle_type", "Char(20)", False),
            ("brand", "Char(50)", False),
            ("color", "Char(20)", False),
            ("owner_name", "Char(100)", False),
            ("owner_phone", "Char(20)", False),
            ("is_blacklisted", "Boolean", False),
            ("blacklist_reason", "Text", False),
            ("remarks", "Text", False),
            ("created_at", "DateTime", False),
            ("updated_at", "DateTime", False),
        ],
        "color": "2F5496",  # 深蓝
    },
    {
        "name": "ExternalVehicle",
        "label": "外来车辆档案",
        "fields": [
            ("plate_number", "Char(20) PK", True),
            ("owner_name", "Char(100)", False),
            ("owner_phone", "Char(20)", False),
            ("created_at", "DateTime", False),
        ],
        "color": "548235",  # 深绿
    },
    {
        "name": "EntryExitRecord",
        "label": "进出记录",
        "fields": [
            ("plate_number", "Char(20)", True),
            ("school_vehicle", "FK→校内车辆", True),
            ("external_vehicle", "FK→外来车辆", True),
            ("record_type", "Char(10)", False),
            ("record_time", "DateTime", False),
            ("driver_name", "Char(50)", False),
            ("driver_phone", "Char(20)", False),
            ("passenger_count", "Integer", False),
            ("goods_info", "Text", False),
            ("purpose", "Text", False),
            ("expected_leave_time", "DateTime", False),
            ("approver", "Char(50)", False),
            ("remarks", "Text", False),
            ("created_at", "DateTime", False),
        ],
        "color": "BF8F00",  # 深金
    },
    {
        "name": "VisitorAppointment",
        "label": "访客预约",
        "fields": [
            ("visitor_name", "Char(50)", True),
            ("visitor_phone", "Char(20)", True),
            ("plate_number", "Char(20)", False),
            ("host_name", "Char(50)", False),
            ("host_department", "Char(100)", False),
            ("expected_time", "DateTime", False),
            ("purpose", "Text", False),
            ("status", "Char(20)", False),
            ("approver", "Char(50)", False),
            ("remarks", "Text", False),
            ("created_at", "DateTime", False),
            ("updated_at", "DateTime", False),
        ],
        "color": "7030A0",  # 深紫
    },
    {
        "name": "NonMotorVehicle",
        "label": "非机动车档案",
        "fields": [
            ("number_plate", "Char(3) PK", True),
            ("vehicle_type", "Char(20)", False),
            ("owner_name", "Char(100)", False),
            ("owner_phone", "Char(20)", False),
            ("brand", "Char(50)", False),
            ("color", "Char(20)", False),
            ("remarks", "Text", False),
            ("created_at", "DateTime", False),
            ("updated_at", "DateTime", False),
        ],
        "color": "C00000",  # 深红
    },
]

# 关联定义
RELATIONS = [
    ("EntryExitRecord", "SchoolVehicle", "school_vehicle"),
    ("EntryExitRecord", "ExternalVehicle", "external_vehicle"),
]

# ---- 页面与布局参数 ----
PAGE_W = 16.54   # A3 横向 (英寸)
PAGE_H = 11.69
MARGIN = 0.6
BOX_W = 4.5
LINE_H = 0.18     # 每行高度
TITLE_H = 0.35    # 标题栏高度
GAP_Y = 0.8       # 实体间垂直间距
GAP_X = 0.5       # 列间距

# 分为两列
# 左列：SchoolVehicle, EntryExitRecord, ExternalVehicle
# 右列：VisitorAppointment, NonMotorVehicle
LEFT_X = MARGIN
RIGHT_X = MARGIN + BOX_W + GAP_X

def entity_height(entity):
    """计算实体框高度"""
    return TITLE_H + len(entity["fields"]) * LINE_H

def layout_entities():
    """计算各实体位置，返回 {name: (x, y, w, h)}"""
    positions = {}

    # 左列：从上到下
    left_entities = ["SchoolVehicle", "EntryExitRecord", "ExternalVehicle"]
    # 右列：从上到下
    right_entities = ["VisitorAppointment", "NonMotorVehicle"]

    # 计算总高度以便居中
    left_total = sum(entity_height(e) for e in ENTITIES if e["name"] in left_entities) + GAP_Y * 2
    right_total = sum(entity_height(e) for e in ENTITIES if e["name"] in right_entities) + GAP_Y * 1

    max_total = max(left_total, right_total)
    start_y = (PAGE_H - max_total) / 2 + max_total  # 从顶部开始

    y = start_y
    for name in left_entities:
        ent = next(e for e in ENTITIES if e["name"] == name)
        h = entity_height(ent)
        y -= h
        positions[name] = (LEFT_X, y, BOX_W, h)
        y -= GAP_Y

    y = start_y
    for name in right_entities:
        ent = next(e for e in ENTITIES if e["name"] == name)
        h = entity_height(ent)
        y -= h
        positions[name] = (RIGHT_X, y, BOX_W, h)
        y -= GAP_Y

    return positions

# ---- XML 工具 ----
def el(tag, **attrs):
    """创建带命名空间的元素"""
    e = Element(f"{{{NS}}}{tag}")
    for k, v in attrs.items():
        e.set(k, str(v))
    return e

def cell(name, value, formula=None):
    """创建 Cell 元素"""
    c = el("Cell", N=name, V=str(value))
    if formula:
        c.set("F", formula)
    return c

def make_xml_declaration():
    return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'

def build_content_types():
    """构建 [Content_Types].xml"""
    root = Element("{http://schemas.openxmlformats.org/package/2006/content-types}Types")
    defaults = [
        ("xml", "application/xml"),
        ("rels", "application/vnd.openxmlformats-package.relationships+xml"),
    ]
    overrides = [
        ("/visio/document.xml", "application/vnd.ms-visio.document.main+xml"),
        ("/visio/pages/pages.xml", "application/vnd.ms-visio.pages+XML"),
        ("/visio/pages/page1.xml", "application/vnd.ms-visio.page+XML"),
        ("/docProps/core.xml", "application/vnd.openxmlformats-package.core-properties+xml"),
        ("/docProps/app.xml", "application/vnd.openxmlformats-officedocument.extended-properties+xml"),
    ]
    for ext, ct in defaults:
        SubElement(root, "{http://schemas.openxmlformats.org/package/2006/content-types}Default",
                   Extension=ext, ContentType=ct)
    for part, ct in overrides:
        SubElement(root, "{http://schemas.openxmlformats.org/package/2006/content-types}Override",
                   PartName=part, ContentType=ct)
    return make_xml_declaration() + tostring(root, encoding="unicode")

def build_rels():
    """构建 _rels/.rels"""
    rels_ns = "http://schemas.openxmlformats.org/package/2006/relationships"
    root = Element(f"{{{rels_ns}}}Relationships")
    items = [
        ("rId1", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties", "docProps/app.xml"),
        ("rId2", "http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties", "docProps/core.xml"),
        ("rId3", "http://schemas.microsoft.com/office/visio/2012/relationships/document", "visio/document.xml"),
    ]
    for rid, rt, target in items:
        SubElement(root, f"{{{rels_ns}}}Relationship", Id=rid, Type=rt, Target=target)
    return make_xml_declaration() + tostring(root, encoding="unicode")

def build_docprops_core():
    """构建 docProps/core.xml"""
    cp_ns = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
    dc_ns = "http://purl.org/dc/elements/1.1/"
    root = Element(f"{{{cp_ns}}}coreProperties")
    SubElement(root, f"{{{dc_ns}}}creator").text = "Codex"
    SubElement(root, f"{{{dc_ns}}}title").text = "实体属性图"
    return make_xml_declaration() + tostring(root, encoding="unicode")

def build_docprops_app():
    """构建 docProps/app.xml"""
    ep_ns = "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
    root = Element(f"{{{ep_ns}}}Properties")
    SubElement(root, f"{{{ep_ns}}}Application").text = "Microsoft Visio"
    SubElement(root, f"{{{ep_ns}}}AppVersion").text = "16.0000"
    return make_xml_declaration() + tostring(root, encoding="unicode")

def build_document_xml():
    """构建 visio/document.xml"""
    root = el("DocumentSettings")
    root.set("xmlns:r", NS_R)
    SubElement(root, f"{{{NS}}}AttachedToolbars").text = ""
    return make_xml_declaration() + tostring(root, encoding="unicode")

def build_pages_xml():
    """构建 visio/pages/pages.xml"""
    root = el("Pages")
    root.set("xmlns:r", NS_R)
    page = SubElement(root, f"{{{NS}}}Page")
    page.set("ID", "0")
    page.set("NameU", "Page-1")
    page.set("Name", "实体属性图")
    page.set("IsCustomNameU", "1")
    SubElement(page, f"{{{NS}}}PageSheet").set("LineStyle", "0")
    return make_xml_declaration() + tostring(root, encoding="unicode")

def build_page1_xml(positions):
    """构建 visio/pages/page1.xml — 核心：实体形状 + 连线"""
    root = el("PageContents")
    root.set("xmlns:r", NS_R)
    root.set("xml:space", "preserve")
    shapes = SubElement(root, f"{{{NS}}}Shapes")

    # 公用样式 ID
    shape_id = 1

    # 实体标题行字符高度
    FONT_SIZE = 0.18  # pt 换算示意，Visio 内部用英寸

    for ent in ENTITIES:
        name = ent["name"]
        label = ent["label"]
        if name not in positions:
            continue
        x, y, w, h = positions[name]
        color = ent["color"]
        fields = ent["fields"]

        # ---- 实体框 Group ----
        group = SubElement(shapes, f"{{{NS}}}Shape")
        group.set("ID", str(shape_id)); shape_id += 1
        group.set("NameU", name)
        group.set("Name", label)
        group.set("Type", "Group")

        SubElement(group, f"{{{NS}}}Cell", N="PinX", V=str(x + w/2))
        SubElement(group, f"{{{NS}}}Cell", N="PinY", V=str(y + h/2))
        SubElement(group, f"{{{NS}}}Cell", N="Width", V=str(w))
        SubElement(group, f"{{{NS}}}Cell", N="Height", V=str(h))
        SubElement(group, f"{{{NS}}}Cell", N="LocPinX", V=str(w/2))
        SubElement(group, f"{{{NS}}}Cell", N="LocPinY", V=str(h/2))

        # --- 主矩形背景 ---
        rect = SubElement(group, f"{{{NS}}}Shape")
        rect.set("ID", str(shape_id)); shape_id += 1
        rect.set("Type", "Shape")
        SubElement(rect, f"{{{NS}}}Cell", N="PinX", V=str(w/2))
        SubElement(rect, f"{{{NS}}}Cell", N="PinY", V=str(h/2))
        SubElement(rect, f"{{{NS}}}Cell", N="Width", V=str(w))
        SubElement(rect, f"{{{NS}}}Cell", N="Height", V=str(h))
        SubElement(rect, f"{{{NS}}}Cell", N="LocPinX", V=str(w/2))
        SubElement(rect, f"{{{NS}}}Cell", N="LocPinY", V=str(h/2))
        SubElement(rect, f"{{{NS}}}Cell", N="FillForegnd", V=f"#{color}")
        SubElement(rect, f"{{{NS}}}Cell", N="FillBkgnd", V=f"#{color}")
        SubElement(rect, f"{{{NS}}}Cell", N="FillPattern", V="1")
        SubElement(rect, f"{{{NS}}}Cell", N="LineColor", V="#333333")
        SubElement(rect, f"{{{NS}}}Cell", N="LineWeight", V="0.01")
        SubElement(rect, f"{{{NS}}}Cell", N="LinePattern", V="1")
        SubElement(rect, f"{{{NS}}}Cell", N="Rounding", V="0.05")

        # 矩形几何
        geo = SubElement(rect, f"{{{NS}}}Section", N="Geometry", IX="0")
        r1 = SubElement(geo, f"{{{NS}}}Row", T="MoveTo", IX="1")
        SubElement(r1, f"{{{NS}}}Cell", N="X", V="0")
        SubElement(r1, f"{{{NS}}}Cell", N="Y", V="0")
        r2 = SubElement(geo, f"{{{NS}}}Row", T="LineTo", IX="2")
        SubElement(r2, f"{{{NS}}}Cell", N="X", V=str(w))
        SubElement(r2, f"{{{NS}}}Cell", N="Y", V="0")
        r3 = SubElement(geo, f"{{{NS}}}Row", T="LineTo", IX="3")
        SubElement(r3, f"{{{NS}}}Cell", N="X", V=str(w))
        SubElement(r3, f"{{{NS}}}Cell", N="Y", V=str(h))
        r4 = SubElement(geo, f"{{{NS}}}Row", T="LineTo", IX="4")
        SubElement(r4, f"{{{NS}}}Cell", N="X", V="0")
        SubElement(r4, f"{{{NS}}}Cell", N="Y", V=str(h))
        r5 = SubElement(geo, f"{{{NS}}}Row", T="LineTo", IX="5")
        SubElement(r5, f"{{{NS}}}Cell", N="X", V="0")
        SubElement(r5, f"{{{NS}}}Cell", N="Y", V="0")

        # --- 标题栏 ---
        title_shape = SubElement(group, f"{{{NS}}}Shape")
        title_shape.set("ID", str(shape_id)); shape_id += 1
        title_shape.set("Type", "Shape")
        SubElement(title_shape, f"{{{NS}}}Cell", N="PinX", V=str(w/2))
        SubElement(title_shape, f"{{{NS}}}Cell", N="PinY", V=str(h - TITLE_H/2))
        SubElement(title_shape, f"{{{NS}}}Cell", N="Width", V=str(w))
        SubElement(title_shape, f"{{{NS}}}Cell", N="Height", V=str(TITLE_H))
        SubElement(title_shape, f"{{{NS}}}Cell", N="LocPinX", V=str(w/2))
        SubElement(title_shape, f"{{{NS}}}Cell", N="LocPinY", V=str(TITLE_H/2))
        SubElement(title_shape, f"{{{NS}}}Cell", N="FillForegnd", V=f"#{color}")
        SubElement(title_shape, f"{{{NS}}}Cell", N="FillBkgnd", V=f"#{color}")
        SubElement(title_shape, f"{{{NS}}}Cell", N="FillPattern", V="1")
        SubElement(title_shape, f"{{{NS}}}Cell", N="LinePattern", V="0")

        # 标题文字样式
        title_char = SubElement(title_shape, f"{{{NS}}}Section", N="Character", IX="0")
        cr = SubElement(title_char, f"{{{NS}}}Row", IX="0")
        SubElement(cr, f"{{{NS}}}Cell", N="Color", V="#FFFFFF")
        SubElement(cr, f"{{{NS}}}Cell", N="Size", V="0.18")
        SubElement(cr, f"{{{NS}}}Cell", N="Style", V="1")  # Bold
        SubElement(cr, f"{{{NS}}}Cell", N="Font", V="Microsoft YaHei")

        title_para = SubElement(title_shape, f"{{{NS}}}Section", N="Paragraph", IX="0")
        pr = SubElement(title_para, f"{{{NS}}}Row", IX="0")
        SubElement(pr, f"{{{NS}}}Cell", N="HorzAlign", V="1")  # Center

        SubElement(title_shape, f"{{{NS}}}Text").text = label

        # --- 属性行 ---
        for i, (fname, ftype, is_key) in enumerate(fields):
            row_y = h - TITLE_H - (i + 0.5) * LINE_H
            row_shape = SubElement(group, f"{{{NS}}}Shape")
            row_shape.set("ID", str(shape_id)); shape_id += 1
            row_shape.set("Type", "Shape")
            SubElement(row_shape, f"{{{NS}}}Cell", N="PinX", V=str(w/2))
            SubElement(row_shape, f"{{{NS}}}Cell", N="PinY", V=str(row_y))
            SubElement(row_shape, f"{{{NS}}}Cell", N="Width", V=str(w))
            SubElement(row_shape, f"{{{NS}}}Cell", N="Height", V=str(LINE_H))
            SubElement(row_shape, f"{{{NS}}}Cell", N="LocPinX", V=str(w/2))
            SubElement(row_shape, f"{{{NS}}}Cell", N="LocPinY", V=str(LINE_H/2))

            # 行背景
            if is_key:
                bg_color = "#DAEEF3"  # 浅蓝（主键行）
            elif i % 2 == 0:
                bg_color = "#F2F2F2"  # 浅灰
            else:
                bg_color = "#FFFFFF"
            SubElement(row_shape, f"{{{NS}}}Cell", N="FillForegnd", V=bg_color)
            SubElement(row_shape, f"{{{NS}}}Cell", N="FillBkgnd", V=bg_color)
            SubElement(row_shape, f"{{{NS}}}Cell", N="FillPattern", V="1")
            SubElement(row_shape, f"{{{NS}}}Cell", N="LinePattern", V="0")

            # 左列：字段名
            left_shape = SubElement(row_shape, f"{{{NS}}}Shape")
            left_shape.set("ID", str(shape_id)); shape_id += 1
            left_shape.set("Type", "Shape")
            SubElement(left_shape, f"{{{NS}}}Cell", N="PinX", V=str(w*0.35))
            SubElement(left_shape, f"{{{NS}}}Cell", N="PinY", V=str(LINE_H/2))
            SubElement(left_shape, f"{{{NS}}}Cell", N="Width", V=str(w*0.65))
            SubElement(left_shape, f"{{{NS}}}Cell", N="Height", V=str(LINE_H))
            SubElement(left_shape, f"{{{NS}}}Cell", N="LocPinX", V="0")
            SubElement(left_shape, f"{{{NS}}}Cell", N="LocPinY", V=str(LINE_H/2))
            SubElement(left_shape, f"{{{NS}}}Cell", N="LinePattern", V="0")
            SubElement(left_shape, f"{{{NS}}}Cell", N="FillPattern", V="0")

            lc = SubElement(left_shape, f"{{{NS}}}Section", N="Character", IX="0")
            lcr = SubElement(lc, f"{{{NS}}}Row", IX="0")
            SubElement(lcr, f"{{{NS}}}Cell", N="Color", V="#000000")
            SubElement(lcr, f"{{{NS}}}Cell", N="Size", V="0.12")
            SubElement(lcr, f"{{{NS}}}Cell", N="Style", V="1" if is_key else "0")
            SubElement(lcr, f"{{{NS}}}Cell", N="Font", V="Microsoft YaHei")

            SubElement(left_shape, f"{{{NS}}}Text").text = fname

            # 右列：类型
            right_shape = SubElement(row_shape, f"{{{NS}}}Shape")
            right_shape.set("ID", str(shape_id)); shape_id += 1
            right_shape.set("Type", "Shape")
            SubElement(right_shape, f"{{{NS}}}Cell", N="PinX", V=str(w*0.75))
            SubElement(right_shape, f"{{{NS}}}Cell", N="PinY", V=str(LINE_H/2))
            SubElement(right_shape, f"{{{NS}}}Cell", N="Width", V=str(w*0.45))
            SubElement(right_shape, f"{{{NS}}}Cell", N="Height", V=str(LINE_H))
            SubElement(right_shape, f"{{{NS}}}Cell", N="LocPinX", V="0")
            SubElement(right_shape, f"{{{NS}}}Cell", N="LocPinY", V=str(LINE_H/2))
            SubElement(right_shape, f"{{{NS}}}Cell", N="LinePattern", V="0")
            SubElement(right_shape, f"{{{NS}}}Cell", N="FillPattern", V="0")

            rc = SubElement(right_shape, f"{{{NS}}}Section", N="Character", IX="0")
            rcr = SubElement(rc, f"{{{NS}}}Row", IX="0")
            SubElement(rcr, f"{{{NS}}}Cell", N="Color", V="#888888")
            SubElement(rcr, f"{{{NS}}}Cell", N="Size", V="0.11")
            SubElement(rcr, f"{{{NS}}}Cell", N="Font", V="Consolas")

            SubElement(right_shape, f"{{{NS}}}Text").text = ftype

    # ---- 关联连线 ----
    for src_name, tgt_name, fk_name in RELATIONS:
        if src_name not in positions or tgt_name not in positions:
            continue
        sx, sy, sw, sh = positions[src_name]
        tx, ty, tw, th = positions[tgt_name]

        # 连线端点：从源底部到目标顶部
        begin_x = sx + sw/2
        begin_y = sy
        end_x = tx + tw/2
        end_y = ty + th

        conn = SubElement(shapes, f"{{{NS}}}Shape")
        conn.set("ID", str(shape_id)); shape_id += 1
        conn.set("NameU", f"Connector_{fk_name}")
        conn.set("Name", fk_name)
        conn.set("Type", "Shape")

        SubElement(conn, f"{{{NS}}}Cell", N="PinX", V=str((begin_x+end_x)/2))
        SubElement(conn, f"{{{NS}}}Cell", N="PinY", V=str((begin_y+end_y)/2))
        SubElement(conn, f"{{{NS}}}Cell", N="BeginX", V=str(begin_x))
        SubElement(conn, f"{{{NS}}}Cell", N="BeginY", V=str(begin_y))
        SubElement(conn, f"{{{NS}}}Cell", N="EndX", V=str(end_x))
        SubElement(conn, f"{{{NS}}}Cell", N="EndY", V=str(end_y))
        SubElement(conn, f"{{{NS}}}Cell", N="LineColor", V="#666666")
        SubElement(conn, f"{{{NS}}}Cell", N="LineWeight", V="0.01")
        SubElement(conn, f"{{{NS}}}Cell", N="LinePattern", V="1")
        SubElement(conn, f"{{{NS}}}Cell", N="BeginArrow", V="0")
        SubElement(conn, f"{{{NS}}}Cell", N="EndArrow", V="5")  # 实心三角箭头

        # 连线几何
        cgeo = SubElement(conn, f"{{{NS}}}Section", N="Geometry", IX="0")
        cr1 = SubElement(cgeo, f"{{{NS}}}Row", T="MoveTo", IX="1")
        SubElement(cr1, f"{{{NS}}}Cell", N="X", V=str(begin_x))
        SubElement(cr1, f"{{{NS}}}Cell", N="Y", V=str(begin_y))
        cr2 = SubElement(cgeo, f"{{{NS}}}Row", T="LineTo", IX="2")
        SubElement(cr2, f"{{{NS}}}Cell", N="X", V=str(end_x))
        SubElement(cr2, f"{{{NS}}}Cell", N="Y", V=str(end_y))

        # FK 标注文字
        label_shape = SubElement(conn, f"{{{NS}}}Shape")
        label_shape.set("ID", str(shape_id)); shape_id += 1
        label_shape.set("Type", "Shape")
        label_x = (begin_x + end_x) / 2 + 0.15
        label_y = (begin_y + end_y) / 2
        SubElement(label_shape, f"{{{NS}}}Cell", N="PinX", V=str(label_x))
        SubElement(label_shape, f"{{{NS}}}Cell", N="PinY", V=str(label_y))
        SubElement(label_shape, f"{{{NS}}}Cell", N="Width", V="2.5")
        SubElement(label_shape, f"{{{NS}}}Cell", N="Height", V="0.2")
        SubElement(label_shape, f"{{{NS}}}Cell", N="LocPinX", V="0")
        SubElement(label_shape, f"{{{NS}}}Cell", N="LocPinY", V="0.1")
        SubElement(label_shape, f"{{{NS}}}Cell", N="LinePattern", V="0")
        SubElement(label_shape, f"{{{NS}}}Cell", N="FillPattern", V="0")

        lc2 = SubElement(label_shape, f"{{{NS}}}Section", N="Character", IX="0")
        lcr2 = SubElement(lc2, f"{{{NS}}}Row", IX="0")
        SubElement(lcr2, f"{{{NS}}}Cell", N="Color", V="#888888")
        SubElement(lcr2, f"{{{NS}}}Cell", N="Size", V="0.10")
        SubElement(lcr2, f"{{{NS}}}Cell", N="Style", V="2")  # Italic
        SubElement(lcr2, f"{{{NS}}}Cell", N="Font", V="Consolas")

        SubElement(label_shape, f"{{{NS}}}Text").text = fk_name

    result = make_xml_declaration() + tostring(root, encoding="unicode")
    # 由于 xml.etree 在处理命名空间时可能重复声明，做后处理
    result = result.replace('xmlns:ns0="' + NS + '"', 'xmlns="' + NS + '"')
    result = result.replace('ns0:', '')
    result = result.replace('<' + NS, '<')
    # 清理重复命名空间
    import re
    result = re.sub(r'\s+xmlns=""', '', result)

    return result

# ---- 构建 ----
def build_vsdx(output_path):
    positions = layout_entities()

    files = {
        "[Content_Types].xml": build_content_types(),
        "_rels/.rels": build_rels(),
        "docProps/app.xml": build_docprops_app(),
        "docProps/core.xml": build_docprops_core(),
        "visio/document.xml": build_document_xml(),
        "visio/pages/pages.xml": build_pages_xml(),
        "visio/pages/page1.xml": build_page1_xml(positions),
    }

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in files.items():
            zf.writestr(name, content.encode("utf-8"))

    print(f"[OK] Generated: {output_path}")
    print(f"   contains {len(ENTITIES)}  entities, {len(RELATIONS)}  relations")

if __name__ == "__main__":
    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "实体属性图.vsdx")
    build_vsdx(output)