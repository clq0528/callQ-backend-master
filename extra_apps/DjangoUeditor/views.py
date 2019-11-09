# coding:utf-8
import os
import json
import random
try:
    # python3
    import urllib.request as urllib
    from urllib.request import urljoin as urljoin
except:
    # python2
    import urllib
    from urllib import basejoin as urljoin
import datetime
from django.http import HttpResponse
from . import settings as USettings
from django.views.decorators.csrf import csrf_exempt
from backend.settings import QINIU_ACCESS_KEY,QINIU_BUCKET_DOMAIN,QINIU_BUCKET_NAME,QINIU_SECRET_KEY,PREFIX_URL
from storages.backends import sftpstorage
import base64

def get_path_format_vars():
    return {
        "year": datetime.datetime.now().strftime("%Y"),
        "month": datetime.datetime.now().strftime("%m"),
        "day": datetime.datetime.now().strftime("%d"),
        "time": datetime.datetime.now().strftime("%H%M%S"),
        "datetime": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
        "rnd": random.randrange(100, 999)
    }


# 保存上传的文件
def save_upload_file(PostFile, FilePath):
    try:
        f = open(FilePath, 'wb')
        for chunk in PostFile.chunks():
            f.write(chunk)
    except Exception as e:
        f.close()
        return u"写入文件错误:%s" % e
    f.close()
    return u"SUCCESS"

# 保存上传到sftp的文件
def save_upload_file_to_sftp(PostFile, FilePath):
    sftp_class = sftpstorage.SFTPStorage()
    save_sftp = sftp_class._save(FilePath,PostFile)
    if save_sftp != FilePath:
        return u"写入文件错误"
    # print(save_sftp)
    # logging.info("sftp return name is ----->"+save_sftp)
    else:
        return u"SUCCESS"


def save_upload_file_to_qiniu(file_data, key):
    access_key = QINIU_ACCESS_KEY
    secret_key = QINIU_SECRET_KEY
    bucket_name = QINIU_BUCKET_NAME
    try:
        from qiniu import Auth, put_file, put_data
        q = Auth(access_key, secret_key)
        token = q.upload_token(bucket_name, key)
        # print(type(upload_file))
        # ret, info = put_file(token, key, upload_file)
        ret, info = put_data(token, key, file_data)
        if ret.get('key', None) == None:
            raise Exception('upload error')
        else:
            return u"SUCCESS"
    except Exception as e:
        # print(str(e))
        return str(e)

@csrf_exempt
def get_ueditor_settings(request):
    return HttpResponse(json.dumps(USettings.UEditorUploadSettings, ensure_ascii=False), content_type="application/javascript")


@csrf_exempt
def get_ueditor_controller(request):
    """获取ueditor的后端URL地址    """

    action = request.GET.get("action", "")
    reponseAction = {
        "config": get_ueditor_settings,
        "uploadimage": UploadFile,
        "uploadscrawl": UploadFile,
        "uploadvideo": UploadFile,
        "uploadfile": UploadFile,
        "catchimage": catcher_remote_image,
        "listimage": list_files,
        "listfile": list_files
    }
    return reponseAction[action](request)


@csrf_exempt
def list_files(request):
    """列出文件"""
    if request.method != "GET":
        return HttpResponse(json.dumps(u"{'state:'ERROR'}"), content_type="application/javascript")
    # 取得动作
    action = request.GET.get("action", "listimage")

    allowFiles = {
        "listfile": USettings.UEditorUploadSettings.get("fileManagerAllowFiles", []),
        "listimage": USettings.UEditorUploadSettings.get("imageManagerAllowFiles", [])
    }
    listSize = {
        "listfile": USettings.UEditorUploadSettings.get("fileManagerListSize", ""),
        "listimage": USettings.UEditorUploadSettings.get("imageManagerListSize", "")
    }
    listpath = {
        "listfile": USettings.UEditorUploadSettings.get("fileManagerListPath", ""),
        "listimage": USettings.UEditorUploadSettings.get("imageManagerListPath", "")
    }
    # 取得参数
    list_size = int(request.GET.get("size", listSize[action]))
    list_start = int(request.GET.get("start", 0))

    files = []
    root_path = os.path.join(USettings.gSettings.MEDIA_ROOT, listpath[action]).replace("\\", "/")
    files = get_files(root_path, root_path, allowFiles[action])

    if (len(files) == 0):
        return_info = {
            "state": u"未找到匹配文件！",
            "list": [],
            "start": list_start,
            "total": 0
        }
    else:
        return_info = {
            "state": "SUCCESS",
            "list": files[list_start:list_start + list_size],
            "start": list_start,
            "total": len(files)
        }

    return HttpResponse(json.dumps(return_info), content_type="application/javascript")


def get_files(root_path, cur_path, allow_types=[]):
    files = []
    items = os.listdir(cur_path)
    for item in items:
        item = unicode(item)
        item_fullname = os.path.join(root_path, cur_path, item).replace("\\", "/")
        if os.path.isdir(item_fullname):
            files.extend(get_files(root_path, item_fullname, allow_types))
        else:
            ext = os.path.splitext(item_fullname)[1]
            is_allow_list = (len(allow_types) == 0) or (ext in allow_types)
            if is_allow_list:
                files.append({
                    "url": urljoin(USettings.gSettings.MEDIA_URL, os.path.join(os.path.relpath(cur_path, root_path), item).replace("\\", "/")),
                    "mtime": os.path.getmtime(item_fullname)
                })

    return files


@csrf_exempt
def UploadFile(request):
    """上传文件"""
    if not request.method == "POST":
        return HttpResponse(json.dumps(u"{'state:'ERROR'}"), content_type="application/javascript")

    state = "SUCCESS"
    action = request.GET.get("action")
    # 上传文件
    upload_field_name = {
        "uploadfile": "fileFieldName", "uploadimage": "imageFieldName",
        "uploadscrawl": "scrawlFieldName", "catchimage": "catcherFieldName",
        "uploadvideo": "videoFieldName",
    }
    UploadFieldName = request.GET.get(upload_field_name[action], USettings.UEditorUploadSettings.get(action, "upfile"))

    # 上传涂鸦，涂鸦是采用base64编码上传的，需要单独处理
    if action == "uploadscrawl":
        upload_file_name = "scrawl.png"
        upload_file_size = 0
    else:
        # 取得上传的文件
        file = request.FILES.get(UploadFieldName, None)
        if file is None:
            return HttpResponse(json.dumps(u"{'state:'ERROR'}"), content_type="application/javascript")
        upload_file_name = file.name
        upload_file_size = file.size

    # 取得上传的文件的原始名称
    upload_original_name, upload_original_ext = os.path.splitext(upload_file_name)

    # 文件类型检验
    upload_allow_type = {
        "uploadfile": "fileAllowFiles",
        "uploadimage": "imageAllowFiles",
        "uploadvideo": "videoAllowFiles"
    }
    if action in upload_allow_type:
        allow_type = list(request.GET.get(upload_allow_type[action], USettings.UEditorUploadSettings.get(upload_allow_type[action], "")))
        if upload_original_ext not in allow_type:
            state = u"服务器不允许上传%s类型的文件。" % upload_original_ext

    # 大小检验
    upload_max_size = {
        "uploadfile": "filwMaxSize",
        "uploadimage": "imageMaxSize",
        "uploadscrawl": "scrawlMaxSize",
        "uploadvideo": "videoMaxSize"
    }
    max_size = int(request.GET.get(upload_max_size[action], USettings.UEditorUploadSettings.get(upload_max_size[action], 0)))
    if max_size != 0:
        from .utils import FileSize
        MF = FileSize(max_size)
        if upload_file_size > MF.size:
            state = u"上传文件大小不允许超过%s。" % MF.FriendValue

    # 检测保存路径是否存在,如果不存在则需要创建
    upload_path_format = {
        "uploadfile": "filePathFormat",
        "uploadimage": "imagePathFormat",
        "uploadscrawl": "scrawlPathFormat",
        "uploadvideo": "videoPathFormat"
    }

    path_format_var = get_path_format_vars()
    path_format_var.update({
        "basename": upload_original_name,
        "extname": upload_original_ext[1:],
        "filename": upload_file_name,
    })
    # 取得输出文件的路径
    OutputPathFormat, OutputPath, OutputFile = get_output_path(request, upload_path_format[action], path_format_var)

    # 所有检测完成后写入文件
    # print('state is --->'+state)
    if state == "SUCCESS":
        if action == "uploadscrawl":
            # state = save_scrawl_file(request, os.path.join(OutputPath, OutputFile))

            #保存到七牛云
            # state = save_scrawl_file_to_qiniu(request, OutputFile)
            #保存到sftp服务器
            state = save_scrawl_file_to_sftp(request, OutputPathFormat,OutputFile)

            return_info = {
                # 保存后的文件名称
                'url': urljoin(USettings.gSettings.MEDIA_URL, 'scram_data/'+ OutputPathFormat),
                # 原始文件名
                'original': upload_file_name,
                'type': upload_original_ext,
                # 上传状态，成功时返回SUCCESS,其他任何值将原样返回至图片上传框中
                'state': state,
                'size': upload_file_size
            }

        else:
            # 保存到文件中，如果保存错误，需要返回ERROR
            #保存到本地
            # state = save_upload_file(file, os.path.join(OutputPath, OutputFile))
            #保存到七牛云
            # state = save_upload_file_to_qiniu(file, OutputPathFormat)
            #保存到sftp服务器上
            state = save_upload_file_to_sftp(file, OutputPathFormat)

            return_info = {
                # 保存后的文件名称
                'url': urljoin(USettings.gSettings.MEDIA_URL, OutputPathFormat),
                # 原始文件名
                'original': upload_file_name,
                'type': upload_original_ext,
                # 上传状态，成功时返回SUCCESS,其他任何值将原样返回至图片上传框中
                'state': state,
                'size': upload_file_size
            }

    # # 返回数据
    # return_info = {
    #     # 保存后的文件名称
    #     'url': urljoin(USettings.gSettings.MEDIA_URL, OutputPathFormat),
    #     # 原始文件名
    #     'original': upload_file_name,
    #     'type': upload_original_ext,
    #     # 上传状态，成功时返回SUCCESS,其他任何值将原样返回至图片上传框中
    #     'state': state,
    #     'size': upload_file_size
    # }

    # # 返回数据
    # QINIU_BUCKET_DOMAIN_URL = PREFIX_URL + QINIU_BUCKET_DOMAIN
    # return_info = {
    #     # 'url': urllib.basejoin(USettings.gSettings.MEDIA_URL , OutputPathFormat) ,                # 保存后的文件名称
    #     'url': urljoin(QINIU_BUCKET_DOMAIN_URL, OutputPathFormat),  # 保存后的文件名称
    #     'original': upload_file_name,  # 原始文件名
    #     'type': upload_original_ext,
    #     'state': state,  # 上传状态，成功时返回SUCCESS,其他任何值将原样返回至图片上传框中
    #     'size': upload_file_size
    # }
    # print('七牛信息---->'+str(return_info))
    return HttpResponse(json.dumps(return_info, ensure_ascii=False), content_type="application/javascript")


@csrf_exempt
def catcher_remote_image(request):
    """远程抓图，当catchRemoteImageEnable:true时，
        如果前端插入图片地址与当前web不在同一个域，则由本函数从远程下载图片到本地
    """
    if not request.method == "POST":
        return HttpResponse(json.dumps(u"{'state:'ERROR'}"), content_type="application/javascript")

    state = "SUCCESS"

    allow_type = list(request.GET.get("catcherAllowFiles", USettings.UEditorUploadSettings.get("catcherAllowFiles", "")))
    max_size = int(request.GET.get("catcherMaxSize", USettings.UEditorUploadSettings.get("catcherMaxSize", 0)))

    remote_urls = request.POST.getlist("source[]", [])
    catcher_infos = []
    path_format_var = get_path_format_vars()

    for remote_url in remote_urls:
        # 取得上传的文件的原始名称
        remote_file_name = os.path.basename(remote_url)
        remote_original_name, remote_original_ext = os.path.splitext(remote_file_name)
        # 文件类型检验
        if remote_original_ext in allow_type:
            path_format_var.update({
                "basename": remote_original_name,
                "extname": remote_original_ext[1:],
                "filename": remote_original_name
            })
            # 计算保存的文件名
            o_path_format, o_path, o_file = get_output_path(request, "catcherPathFormat", path_format_var)
            o_filename = os.path.join(o_path, o_file).replace("\\", "/")
            # 读取远程图片文件
            try:
                remote_image = urllib.urlopen(remote_url)
                # 将抓取到的文件写入文件
                try:
                    f = open(o_filename, 'wb')
                    f.write(remote_image.read())
                    f.close()
                    state = "SUCCESS"
                except Exception as e:
                    state = u"写入抓取图片文件错误:%s" % e
            except Exception as e:
                state = u"抓取图片错误：%s" % e

            catcher_infos.append({
                "state": state,
                "url": urljoin(USettings.gSettings.MEDIA_URL, o_path_format),
                "size": os.path.getsize(o_filename),
                "title": os.path.basename(o_file),
                "original": remote_file_name,
                "source": remote_url
            })

    return_info = {
        "state": "SUCCESS" if len(catcher_infos) > 0 else "ERROR",
        "list": catcher_infos
    }

    return HttpResponse(json.dumps(return_info, ensure_ascii=False), content_type="application/javascript")


def get_output_path(request, path_format, path_format_var):
    # 取得输出文件的路径
    OutputPathFormat = (request.GET.get(path_format, USettings.UEditorSettings["defaultPathFormat"]) % path_format_var).replace("\\", "/")
    # 分解OutputPathFormat
    OutputPath, OutputFile = os.path.split(OutputPathFormat)
    OutputPath = os.path.join(USettings.gSettings.MEDIA_ROOT, OutputPath)
    # 如果OutputFile为空说明传入的OutputPathFormat没有包含文件名，因此需要用默认的文件名
    if not OutputFile:
        OutputFile = USettings.UEditorSettings["defaultPathFormat"] % path_format_var
        OutputPathFormat = os.path.join(OutputPathFormat, OutputFile)
    if not os.path.exists(OutputPath):
        os.makedirs(OutputPath)
    return (OutputPathFormat, OutputPath, OutputFile)


# 涂鸦功能上传处理
@csrf_exempt
def save_scrawl_file(request, filename):
    try:
        content = request.POST.get(USettings.UEditorUploadSettings.get("scrawlFieldName", "upfile"))
        f = open(filename, 'wb')
        f.write(base64.b64decode(content))
        f.close()
        state = "SUCCESS"
    except Exception as e:
        state = u"写入图片文件错误:%s" % e
    return state

#涂鸦七牛云功能上传处理
@csrf_exempt
def save_scrawl_file_to_qiniu(request, filename):
    access_key = QINIU_ACCESS_KEY
    secret_key = QINIU_SECRET_KEY
    bucket_name = QINIU_BUCKET_NAME
    try:
        from qiniu import Auth, put_file, put_data
        q = Auth(access_key, secret_key)
        token = q.upload_token(bucket_name, filename)
        # ret, info = put_file(token, key, upload_file)
        content = request.POST.get(USettings.UEditorUploadSettings.get("scrawlFieldName", "upfile"))
        content = base64.b64decode(content)
        ret, info = put_data(token, filename, content)
        if ret.get('key', None) == None:
            raise Exception('upload error')
        else:
            return u"SUCCESS"
    except Exception as e:
        return str(e)

# 保存上传到sftp的文件
#这个savepath暂时只能是根目录，如果保存早其他目录，显示的时候会因为目录的原因找不到路径
#修改了sftp_class._save方法，可以直接传base64图片数据
@csrf_exempt
def save_scrawl_file_to_sftp(request, savepath, filename):
    savepath = 'scram_data/' + savepath
    content = request.POST.get(USettings.UEditorUploadSettings.get("scrawlFieldName", "upfile"))
    sftp_class = sftpstorage.SFTPStorage()
    save_sftp = sftp_class._save(savepath,filename,base64.b64decode(content))
    if save_sftp != savepath:
        return u"写入文件错误"
    else:
        return u"SUCCESS"