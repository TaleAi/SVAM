from hashlib import md5
from random import randint
from time import sleep
from os import path

from moviepy.editor import *
from loguru import logger


class ContentMaker:
    def __init__(self):
        from api_server.storage.mysql import SqlAction
        from api_server.storage.rabbitmq import Mq
        self.mysql = SqlAction()
        self.parent_dir = os.path.dirname(os.path.abspath(__file__))

    def make_sister_video(self, clip_dict, uuid):
        # 生成开头
        start_clip_dict = clip_dict.copy()
        for i in range(min(len(clip_dict), 9), 9):
            start_clip_dict[f'clip{i + 1}'] = clip_dict[f'clip{i%len(clip_dict)+1}']
        use_clip = []
        # 九宫格
        for i in range(0, 9, 3):
            use_clip.append(
                [start_clip_dict[f'clip{i + 1}'].resize(width=360).fx(afx.volumex, 0.08),
                 start_clip_dict[f'clip{i + 2}'].resize(
                     width=360).fx(afx.volumex, 0.08),
                 start_clip_dict[f'clip{i + 3}'].resize(width=360).fx(afx.volumex, 0.08)])
        start = clips_array(use_clip).subclip(0, 5).fx(
            vfx.fadeout, 1.5).fx(afx.audio_fadeout, 3).set_fps(30)
        start.write_videofile(
            f'/mnt/l1/short_video/tmp/{uuid}_start.mp4', threads=1)
        start = VideoFileClip(f'/mnt/l1/short_video/tmp/{uuid}_start.mp4')
        txt_clip = VideoFileClip(os.path.join(
            self.parent_dir, 'text.mp4')).set_fps(30)
        now = 8
        for index, item in enumerate(clip_dict):
            if item == 'clip1':
                clip_dict[f"clip{index+1}"] = clip_dict[f"clip{index+1}"].set_start(
                    now)
                continue
            clip_dict[f"clip{index+1}"] = clip_dict[f"clip{index+1}"].set_start(
                now+clip_dict[f"clip{index}"].end-clip_dict[f"clip{index}"].start)
            now += clip_dict[f"clip{index}"].end - \
                clip_dict[f"clip{index}"].start
        now += clip_dict[f"clip{index+1}"].end - \
            clip_dict[f"clip{index+1}"].start
        # main = concatenate_videoclips(list(clip_dict.values()))
        before = [start, txt_clip.set_pos('center').set_start(3.5)]
        before.extend(list(clip_dict.values()))
        main = CompositeVideoClip(before)
        return main

    def sister(self, count):
        while count:
            origin_clips, selected_list = self.get_origin_clips(
                '抖音', '小姐姐', '小姐姐')
            selected_list.sort()
            uuid = md5(str(selected_list).encode(encoding="utf-8")).hexdigest()
            title = uuid[:10]
            video = self.make_sister_video(origin_clips, uuid)
            save_path = '/mnt/l1/short_video/creation/' + title + '.mp4'
            video.write_videofile(save_path, threads=1)
            used_uuid = ''
            for id in selected_list:
                used_uuid += id[:10] + "|"
                old = self.mysql.get_data_from_mysql(
                    'source_info', 'used_time', f"uuid='{id}'")
                self.mysql.update_data_into_mysql(
                    'source_info', f'used_time={old + 1}', f"uuid='{id}'")
            upname = ''
            name_space = {'name_space0': ['😀', '😃', '😄', '😁', '😆'], 
                            'name_space1': ['你喜欢的', '兄弟们来看', '这就是你想要的', '今日份', '别眨眼，', '艾特你的列表来看', '快看！', '今日限定！', '喜欢', '选一个'],
                            'name_space2': ['天生丽质', '亭亭玉立', '袅娜娉婷', '国色天香', '可爱', '漂亮', '正点聪慧', '醒目', '善良', '机灵', '有气质', '清秀', '清纯', '美艳', '有魅力', '绝代佳人', '仙姿佚貌', '冰肌玉骨', '眉目如画', '环肥燕瘦',
                                            '眉清目秀', '千娇百媚', '梨花带雨', '宛转蛾眉', '靡颜腻理', '粉妆玉琢', '月里嫦娥', '国色天姿', '玉貌花容', '秀外惠中', '仙姿玉貌', '美若天仙', '美愈天人', '貌赛西施', '美艳绝世', '清艳脱俗', '妖娆动人', '淡扫峨眉', '螓首蛾眉'],
                            'name_space3': ['の', 'de', '的', '的', '的', '的', '的', '的', '的', '的'], 
                            'name_space4': ['小姐姐', '小姐姐们'], 
                            'name_space5': ['😀', '😃', '😄', '😁', '😆', '😅', '🤣', '😂', '🙂', '😉', '😊', '😇', '🥰', '😍', '🤩', '😘', '😗', '😚', '😙', '😋', '😛', '😜', '🤪', '😝', '🤗', '🤭', '🤫', '🤔', '🤐', '🤨', '😐', '😑', '😶', '😏', '😬', '🤥', '😌', '🤤', '🥴', '🤯', '🤠', '🥳', '🥸', '😎', '🤓', '😮', '😯', '😲', '😳', '🥺'],
                            'name_space6': ['🐵', '🐒', '🦍', '🦧', '🐕', '🦮', '🐕','🦺', '🐩', '🐺', '🦊', '🦝', '🐱', '🐈', '🐈', '🦁', '🐯', '🐅', '🐆', '🦄', '🦓', '🦌', '🦬', '*', '🐂', '🐃', '🐄', '🐷', '🐖', '🐗', '🐽', '🐏', '🐑', '🐐', '🐪', '🐫', '🦙', '🦒', '🐘', '🦣', '🦏', '🦛', '🐭', '🐁', '🐀', '🐹', '🐰', '🐇', '🐿', '🦫', '🦔', '🐨', '🐼', '🦥', '🦦', '🦨', '🦘', '🦡', '🐾', '🦃', '🐔', '🐓', '🐣', '🐤', '🐥', '🐦', '🦅', '🦆', '🦢', '🦉', '🦤', '🪶', '🦩', '🦚', '🦜', '🐸', '🐊', '*', '🦎', '🐍', '🐲', '🐉', '🦕', '🦖', '🐳', '🐋', '🐬', '🦭', '🐟', '🐡', '🦈', '🐙']
                            }
            for i in range(7):
                upname += name_space[f'name_space{i}'][randint(0, len(name_space[f'name_space{i}'])-1)]
            self.mysql.insert_data_into_mysql('creation(uuid,path,direction,used_sources,file_name,title)',
                                              f"('{uuid}','{save_path}','小姐姐','{used_uuid}','{title + '.mp4'}','{upname}')")

    def add_field_name(self, single_data, param_list):
        if len(single_data) != len(param_list):
            logger.error(f'数据长度不一致,数据:{single_data},字段列表:{param_list}')
            raise Exception(f'数据长度不一致,数据:{single_data},字段列表:{param_list}')
        return dict(zip(param_list, single_data))

    def get_origin_clips(self, data_type, inner_type, style):
        raw_data = self.mysql.get_data_from_mysql(table='source_info', data_name='*',
                                                  condition=f"data_type='{data_type}' and inner_type='{inner_type}' and style='{style}' and is_deleted!='1' and main_file!='NULL'")
        mysql_data = []
        for i in raw_data:
            mysql_data.append(self.add_field_name(i, ['id', 'uuid', 'title', 'is_deleted', 'data_type', 'inner_type',
                                                      'style', 'origin_time', 'used_time', 'main_file', 'link_1',
                                                      'link_2', 'link_3',
                                                      'link_4']))
        if len(mysql_data) < 50:
            logger.info("素材数量不够")
            sleep(100)
            return 0
        else:
            start_count = 0
            end_count = len(mysql_data) - 1
            total_lenth = 0.0
            count = 0
            clip_dict = {}
            selected_list = []
            while total_lenth < 90:
                select = mysql_data[randint(start_count, end_count)]
                temp_clip = VideoFileClip(select['main_file'])
                if temp_clip.end > 10:
                    clip = temp_clip.subclip(0, 10).set_pos('center').fx(vfx.fadein, 0.5).fx(
                        vfx.fadeout, 0.5).fx(afx.audio_fadeout, 1).set_fps(30).resize(width=1080)
                    total_lenth += 10
                elif temp_clip.end < 3:
                    continue
                else:
                    clip = temp_clip.set_pos('center').fx(vfx.fadein, 0.5).fx(
                        vfx.fadeout, 0.5).fx(afx.audio_fadeout, 1).set_fps(30).resize(width=1080)
                    total_lenth += temp_clip.end
                count += 1
                clip_dict[f'clip{count}'] = clip
                selected_list.append(select['uuid'])
        return clip_dict, selected_list


content_maker = ContentMaker()
