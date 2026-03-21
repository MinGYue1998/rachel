"""
工具定义（Function Calling Schema）
定义所有可用的工具，供Qwen模型调用
"""

from typing import List, Dict, Any

# 工具定义列表
TOOLS: List[Dict[str, Any]] = [
    # ==================== 只读工具（查询类）====================
    {
        "type": "function",
        "function": {
            "name": "query_students",
            "description": "查询学生列表，可根据姓名或状态筛选",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "学生姓名（模糊匹配，可选）"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["active", "inactive"],
                        "description": "学生状态：active（在读）或 inactive（已停用），可选"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_student_detail",
            "description": "获取学生详细信息，包括基本信息、课程、费用等。如果不知道学生ID，可以通过姓名查询",
            "parameters": {
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "integer",
                        "description": "学生ID（优先使用）"
                    },
                    "student_name": {
                        "type": "string",
                        "description": "学生姓名（如果不知道ID，使用姓名查询）"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_courses",
            "description": "查询课程列表",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "课程名称（模糊匹配，可选）"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_class_records",
            "description": "查询上课记录，可按学生、课程、日期范围筛选",
            "parameters": {
                "type": "object",
                "properties": {
                    "student_name": {
                        "type": "string",
                        "description": "学生姓名（可选）"
                    },
                    "course_name": {
                        "type": "string",
                        "description": "课程名称（可选）"
                    },
                    "date_from": {
                        "type": "string",
                        "description": "开始日期，格式：YYYY-MM-DD（可选）"
                    },
                    "date_to": {
                        "type": "string",
                        "description": "结束日期，格式：YYYY-MM-DD（可选）"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_fees",
            "description": "查询费用记录",
            "parameters": {
                "type": "object",
                "properties": {
                    "student_name": {
                        "type": "string",
                        "description": "学生姓名（可选）"
                    },
                    "course_name": {
                        "type": "string",
                        "description": "课程名称（可选）"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_arrears_students",
            "description": "查询欠费学生列表，返回所有有欠费的学生",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_monthly_report",
            "description": "查询月度汇总报表",
            "parameters": {
                "type": "object",
                "properties": {
                    "year": {
                        "type": "integer",
                        "description": "年份，如：2024（可选，默认当前年）"
                    },
                    "month": {
                        "type": "integer",
                        "description": "月份，1-12（可选，默认当前月）"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_student_detail_report",
            "description": "查询学生明细报表",
            "parameters": {
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "integer",
                        "description": "学生ID（可选）"
                    },
                    "course_id": {
                        "type": "integer",
                        "description": "课程ID（可选）"
                    },
                    "year": {
                        "type": "integer",
                        "description": "年份（可选）"
                    },
                    "month": {
                        "type": "integer",
                        "description": "月份，1-12（可选）"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前日期和时间，用于填写各种添加时间。返回格式：YYYY-MM-DD HH:MM:SS",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weekday_dates",
            "description": "获取当月某个星期几的所有日期。例如：传入2，返回当月所有星期二的日期列表",
            "parameters": {
                "type": "object",
                "properties": {
                    "weekday": {
                        "type": "integer",
                        "description": "星期几，1=星期一，2=星期二，...，7=星期日"
                    }
                },
                "required": ["weekday"]
            }
        }
    },

    # ==================== 写操作工具（需要用户确认）====================
    {
        "type": "function",
        "function": {
            "name": "create_student",
            "description": "【需要确认】新增学生。创建学生档案，包含基本信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "学生姓名"
                    },
                    "phone": {
                        "type": "string",
                        "description": "联系电话（可选）"
                    },
                    "gender": {
                        "type": "string",
                        "enum": ["男", "女"],
                        "description": "性别（可选）"
                    },
                    "guardian": {
                        "type": "string",
                        "description": "监护人姓名（可选）"
                    },
                    "guardian_phone": {
                        "type": "string",
                        "description": "监护人电话（可选）"
                    },
                    "address": {
                        "type": "string",
                        "description": "家庭住址（可选）"
                    },
                    "remark": {
                        "type": "string",
                        "description": "备注（可选）"
                    }
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_course",
            "description": "【需要确认】新增课程。创建课程，设置课时单价和授课老师",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "课程名称"
                    },
                    "unit_price": {
                        "type": "number",
                        "description": "课时单价，如：100.00"
                    },
                    "teacher": {
                        "type": "string",
                        "description": "授课老师（可选）"
                    },
                    "description": {
                        "type": "string",
                        "description": "课程描述（可选）"
                    }
                },
                "required": ["name", "unit_price"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_class_record",
            "description": "【需要确认】创建一条上课记录。此操作将：1）创建上课记录；2）增加学生课时；3）产生课时费用",
            "parameters": {
                "type": "object",
                "properties": {
                    "student_name": {
                        "type": "string",
                        "description": "学生姓名"
                    },
                    "course_name": {
                        "type": "string",
                        "description": "课程名称"
                    },
                    "class_date": {
                        "type": "string",
                        "description": "上课日期，格式：YYYY-MM-DD"
                    },
                    "class_hours": {
                        "type": "number",
                        "description": "课时数，如：2.0"
                    },
                    "content": {
                        "type": "string",
                        "description": "上课内容（可选）"
                    }
                },
                "required": ["student_name", "course_name", "class_date", "class_hours"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "batch_create_class_records",
            "description": "【需要确认】批量创建上课记录（最多10条）。此操作将批量增加课时和费用",
            "parameters": {
                "type": "object",
                "properties": {
                    "records": {
                        "type": "array",
                        "description": "上课记录列表",
                        "items": {
                            "type": "object",
                            "properties": {
                                "student_name": {"type": "string"},
                                "course_name": {"type": "string"},
                                "class_date": {"type": "string"},
                                "class_hours": {"type": "number"}
                            },
                            "required": ["student_name", "course_name", "class_date", "class_hours"]
                        },
                        "maxItems": 10
                    }
                },
                "required": ["records"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_student_discount",
            "description": "【需要确认】更新学生在某课程的优惠金额。此操作将影响费用计算",
            "parameters": {
                "type": "object",
                "properties": {
                    "student_name": {
                        "type": "string",
                        "description": "学生姓名"
                    },
                    "course_name": {
                        "type": "string",
                        "description": "课程名称"
                    },
                    "discount": {
                        "type": "number",
                        "description": "优惠金额，如：100.00"
                    }
                },
                "required": ["student_name", "course_name", "discount"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_payment",
            "description": "【需要确认】登记缴费记录。此操作将减少学生的欠费金额",
            "parameters": {
                "type": "object",
                "properties": {
                    "student_name": {
                        "type": "string",
                        "description": "学生姓名"
                    },
                    "amount": {
                        "type": "number",
                        "description": "缴费金额，如：500.00"
                    },
                    "payment_method": {
                        "type": "string",
                        "enum": ["cash", "wechat", "alipay", "bank_transfer"],
                        "description": "支付方式：cash（现金）、wechat（微信）、alipay（支付宝）、bank_transfer（银行转账）"
                    },
                    "remark": {
                        "type": "string",
                        "description": "备注（可选）"
                    }
                },
                "required": ["student_name", "amount", "payment_method"]
            }
        }
    }
]

# 写操作工具名称列表（用于判断是否需要确认）
WRITE_TOOLS = {
    "create_student",
    "create_course",
    "create_class_record",
    "batch_create_class_records",
    "update_student_discount",
    "create_payment",
}


def is_write_tool(tool_name: str) -> bool:
    """判断是否为写操作工具"""
    return tool_name in WRITE_TOOLS


def get_tool_by_name(tool_name: str) -> Dict[str, Any]:
    """根据名称获取工具定义"""
    for tool in TOOLS:
        if tool["function"]["name"] == tool_name:
            return tool
    return {}
