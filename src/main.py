import argparse
from crawler import XHSCrawler
from loguru import logger

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='小红书内容提取工具')
    parser.add_argument('--keyword', '-k', type=str, required=True, help='搜索关键词')
    parser.add_argument('--pages', '-p', type=int, default=1, help='爬取页数')
    parser.add_argument('--config', '-c', type=str, default='config.py', help='配置文件路径')
    args = parser.parse_args()

    try:
        # 初始化爬虫
        crawler = XHSCrawler(config_path=args.config)
        all_notes = []

        # 搜索笔记
        for page in range(1, args.pages + 1):
            notes = crawler.search_notes(args.keyword, page)
            logger.info(f"第 {page} 页搜索到 {len(notes)} 条笔记")
            
            # 获取笔记详情
            for note in notes:
                detail = crawler.get_note_detail(note['id'], note.get('url'))
                if detail:
                    all_notes.append(detail)
                crawler.random_delay()

        # 保存数据到CSV
        if all_notes:
            output_filename = f"{args.keyword}_results.csv"
            crawler.save_to_csv(all_notes, output_filename)
            logger.info("爬取完成")
        else:
            logger.warning("未获取到任何笔记详情")

    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
        raise

if __name__ == "__main__":
    main() 