from django.contrib.auth import get_user_model
from io import BytesIO
import xlsxwriter

from core.models import Order
from core.constants import ITEM_NAMES

User = get_user_model()

COMMON_COLOR = "#82CD47"
WHITE = "#fff"
BOX_LABLES = [
    "500 GM",
    "1 KG",
]
COLORS = [
    "#FFD933",
    "#33FFD9",
    "#FF33FF",
    "#33D9FF",
    "#FF6633",
    "#33FF66",
    "#FF9933",
    "#3399FF",
    "#FF3399",
    "#99FF33",
    "#33CCFF",
    "#FFCC33",
    "#33FFCC",
    "#FF5733",
    "#33FF57",
    "#3366FF",
    "#FF33B8",
    "#33FFFF",
    "#FF3366",
    "#66FF33",
]


def extract_data(pack):
    data = {}
    return data


EXPORT_FORMAT = [
    {
        "title": "Bill Number",
        "col-type": "single",
        "bg-color": COMMON_COLOR,
        "text-color": WHITE,
        "key": "bill_number",
        "pre-func": lambda x: x,
    },
    {
        "title": "Name",
        "col-type": "single",
        "bg-color": COMMON_COLOR,
        "text-color": WHITE,
        "key": "customer_name",
        "pre-func": lambda x: x,
    },
    {
        "title": "Address",
        "col-type": "span",
        "bg-color": COMMON_COLOR,
        "text-color": WHITE,
        "key": "items",
        "child": ITEM_NAMES[0],
        "pre-func": extract_data,
    },
    {
        "title": "Total Amount",
        "col-type": "single",
        "bg-color": COMMON_COLOR,
        "text-color": WHITE,
        "key": "total_amount",
        "pre-func": lambda x: x,
    },
]


def write_orders_data(worksheet, excel_file, data):
    DATA_CELL_FORMAT = excel_file.add_format(
        {
            "align": "center",
            "valign": "vcenter",
            "border": 1,
        }
    )

    curr_row, curr_col = 0, 0
    worksheet.merge_range(
        0,
        0,
        1,
        0,
        "Bill Number",
        excel_file.add_format(
            {
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "font_size": "14",
                "bg_color": COMMON_COLOR,
                "border": 1,
            }
        ),
    )
    worksheet.merge_range(
        0,
        1,
        1,
        1,
        "Name",
        excel_file.add_format(
            {
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "font_size": "14",
                "bg_color": COMMON_COLOR,
                "border": 1,
            }
        ),
    )
    col = 2
    color = 0
    for item in ITEM_NAMES[0]:
        if len(item[1]) == 1:
            worksheet.write(
                0,
                col,
                item[0],
                excel_file.add_format(
                    {
                        "bold": True,
                        "align": "center",
                        "valign": "vcenter",
                        "font_size": "14",
                        "bg_color": COLORS[color],
                        "border": 1,
                    }
                ),
            )

        else:
            worksheet.merge_range(
                0,
                col,
                0,
                col + len(item[1]) - 1,
                item[0],
                excel_file.add_format(
                    {
                        "bold": True,
                        "align": "center",
                        "valign": "vcenter",
                        "font_size": "14",
                        "bg_color": COLORS[color],
                        "border": 1,
                    }
                ),
            )
        for pack in item[1]:
            worksheet.write(
                1,
                col,
                pack,
                excel_file.add_format(
                    {
                        "bold": True,
                        "align": "center",
                        "valign": "vcenter",
                        "font_size": "14",
                        "bg_color": COLORS[color],
                        "border": 1,
                    }
                ),
            )
            col += 1

        color += 1
        color = color % len(COLORS)

    worksheet.merge_range(
        0,
        col,
        1,
        col,
        "Total Amount",
        excel_file.add_format(
            {
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "font_size": "14",
                "bg_color": COMMON_COLOR,
                "border": 1,
            }
        ),
    )
    curr_row = 2

    for d in data:
        col = 0
        worksheet.write(
            curr_row,
            col,
            d["bill_number"],
            DATA_CELL_FORMAT,
        )
        col += 1
        worksheet.write(
            curr_row,
            col,
            d["customer_name"],
            DATA_CELL_FORMAT,
        )
        col += 1
        for item in ITEM_NAMES[1]:
            worksheet.write(
                curr_row,
                col,
                d[item] or 0,
                DATA_CELL_FORMAT,
            )
            col += 1
        worksheet.write(
            curr_row,
            col,
            d["total_amount"],
            DATA_CELL_FORMAT,
        )


def export_data():
    with BytesIO() as output:
        SHEET_NAME = "Orders"
        excel_file = xlsxwriter.Workbook(output)
        worksheet = excel_file.add_worksheet(SHEET_NAME)
        data = Order.objects.prefetch_related("dealer").all().values()
        write_orders_data(worksheet, excel_file, data)
        excel_file.close()
        output.seek(0)
        return output.read()
