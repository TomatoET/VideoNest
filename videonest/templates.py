from __future__ import annotations


DIRECTORY_TEMPLATE: tuple[str, ...] = (
    "00_导出/成片",
    "00_导出/小样",
    "01_视频/A-Roll_口播",
    "01_视频/B-Roll_补充画面",
    "01_视频/其他素材",
    "02_图片/封面",
    "02_图片/包装设计素材",
    "02_图片/图片素材",
    "03_音频/BGM",
    "03_音频/音效",
    "03_音频/录音",
    "04_工程文件/剪映",
    "04_工程文件/Premiere",
    "04_工程文件/达芬奇",
    "05_脚本/口播稿",
    "05_脚本/分镜",
    "05_脚本/拍摄清单",
    "99_参考资料",
)


ASSET_CSV_HEADER = "文件名,素材类型,来源,用途,是否已使用,备注\n"


def project_readme_content(project_name: str, created_date: str) -> str:
    return f"""# 项目说明

- 项目名称：{project_name}
- 创建日期：{created_date}
- 视频主题：
- 发布平台：
- 当前状态：筹备中
- 备注：
"""


SHOOTING_LIST_CONTENT = """# 拍摄清单

- [ ] 开场画面
- [ ] 产品特写
- [ ] 操作过程
- [ ] 细节补拍
- [ ] 结尾画面
"""
