import logging
import requests
import datetime
import json
import time

# 定义__all__变量，指定可以被导出的名称
__all__ = ['视奸编程猫论坛', '视奸用户列表里所有用户']

def 视奸编程猫论坛():
    # 记录上一次的帖子标题，用于检测变化
    previous_title = None
    i = 0
    
    logging.info("由于技术问题，您需要手动输入起始项，防止访问置顶帖")
    try:
        start_id = int(input("请输入起始项ID（从1开始）："))
    except ValueError:
        logging.error("请输入有效的数字")
        return
    
    while True:
        i += 1
        logging.info(f"第{i}次获取论坛信息")
        
        try:
            # 获取热门帖子列表
            res = requests.get("https://api.codemao.cn/web/forums/posts/hots/all")
            res.raise_for_status()
            
            items = res.json()['items']
            
            # 检查起始项是否有效
            if start_id - 1 >= len(items):
                logging.error(f"起始项 {start_id} 超出范围，最大为 {len(items)}")
                return
            
            post_id = items[start_id - 1]
            logging.info(f"获取到帖子ID: {post_id}")
            
            # 获取帖子详情
            res2 = requests.get(f"https://api.codemao.cn/web/forums/posts/all?ids={post_id}")
            res2.raise_for_status()
            
            post_data = res2.json()['items']
            
            if not post_data or len(post_data) == 0:
                logging.warning("未获取到帖子详情")
                time.sleep(10)
                continue
                
            post = post_data[0]
            title = post.get('title', '无标题')
            content = post.get('content', '无内容')
            timestamp = post.get('created_at', 0)
            
            utc8_time = datetime.datetime.fromtimestamp(
                timestamp, 
                tz=datetime.timezone(datetime.timedelta(hours=8))
            )
            
            # 检查是否有新帖子
            if previous_title is None:
                logging.info("最新帖子（首次获取）：")
                logging.info(f"标题：{title}")
                logging.info(f"内容：{content}")
                logging.info(f"发布时间：{utc8_time}")
                previous_title = title
            elif title != previous_title:
                logging.info("发现新帖子：")
                logging.info(f"标题：{title}")
                logging.info(f"内容：{content}")
                logging.info(f"发布时间：{utc8_time}")
                previous_title = title
            else:
                logging.info("最新帖子没有变化")
                
        except requests.RequestException as e:
            logging.error(f"获取数据失败: {e}")
        except Exception as e:
            logging.error(f"处理数据时发生错误: {e}")
        
        time.sleep(10)

def 视奸用户列表里所有用户():
    try:
        with open('UserConfig.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            user_list = data['user_list']
    except FileNotFoundError:
        logging.error("UserConfig.json 文件不存在")
        return
    except KeyError:
        logging.error("UserConfig.json 格式错误，缺少 'user_list' 字段")
        return
    
    # 为每个用户创建一个最新的记录字典
    # 格式：{用户ID: 该用户上一次查询到的最新作品名称}
    user_latest_work = {}
    
    i = 0
    while True:
        i += 1
        logging.info(f"第{i}次获取用户作品")
        
        for user_id in user_list:
            logging.info(f"正在查询用户ID: {user_id}")
            
            try:
                response = requests.get(
                    f'https://api.codemao.cn/creation-tools/v1/user/center/work-list?'
                    f'user_id={user_id}&offset=0&limit=1'  # 只获取最新的一件作品
                )
                response.raise_for_status()  # 检查请求是否成功
                
                work_data = response.json()
                
                if work_data['items'] and len(work_data['items']) > 0:
                    latest_work = work_data['items'][0]
                    
                    work_id = latest_work['id']
                    work_name = latest_work['work_name']
                    description = latest_work['description']
                    timestamp = latest_work['publish_time']
                    
                    utc8_time = datetime.datetime.fromtimestamp(
                        timestamp, 
                        tz=datetime.timezone(datetime.timedelta(hours=8))
                    )
                    
                    # 检查这个用户是否有上一次的记录
                    if user_id not in user_latest_work:
                        # 第一次查询这个用户，直接记录并显示
                        user_latest_work[user_id] = work_name
                        logging.info(f"用户 {user_id} 最新作品：")
                        logging.info(f"  作品ID：{work_id}")
                        logging.info(f"  作品名称：{work_name}")
                        logging.info(f"  描述：{description}")
                        logging.info(f"  发布时间：{utc8_time}")
                    else:
                        # 不是第一次查询，检查是否有更新
                        if work_name != user_latest_work[user_id]:
                            logging.info(f"用户 {user_id} 发布了新作品：")
                            logging.info(f"  作品ID：{work_id}")
                            logging.info(f"  作品名称：{work_name}")
                            logging.info(f"  描述：{description}")
                            logging.info(f"  发布时间：{utc8_time}")
                            
                            # 更新这个用户的最新作品记录
                            user_latest_work[user_id] = work_name
                        else:
                            logging.info(f"用户 {user_id} 的最新作品没有变化")
                else:
                    logging.info(f"用户 {user_id} 没有发布过作品")
                    
            except requests.RequestException as e:
                logging.error(f"查询用户 {user_id} 失败: {e}")
            except KeyError as e:
                logging.error(f"解析用户 {user_id} 数据失败，缺少字段: {e}")
            except Exception as e:
                logging.error(f"处理用户 {user_id} 时发生未知错误: {e}")
        
        logging.info("本轮查询完成，等待10秒后继续...")
        time.sleep(10)