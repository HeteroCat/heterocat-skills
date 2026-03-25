#!/usr/bin/env python3
"""
Doubao Seedance Video Generation - API Client
"""
import json
import time
import urllib.request
import urllib.error
from typing import Optional, Dict, Any

from config import API_BASE_URL, API_KEY, POLL_INTERVAL, MAX_POLL_TIME
from utils import print_info, print_success, print_error, print_progress


class DoubaoVideoAPI:
    """Doubao Seedance Video Generation API Client"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or API_KEY
        self.base_url = API_BASE_URL

        if not self.api_key:
            raise ValueError("API Key is required. Use -k parameter or set ARK_API_KEY environment variable.")

    def _make_request(self, endpoint: str, data: Optional[Dict] = None, method: str = "POST") -> Dict:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8") if data else None,
            headers=headers,
            method=method,
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            raise Exception(f"HTTP Error {e.code}: {error_body}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

    def create_task(
        self,
        model: str,
        content: list,
        duration: int = 5,
        ratio: str = "adaptive",
        resolution: str = "720p",
        generate_audio: bool = True,
        camera_fixed: bool = False,
        watermark: bool = False,
        seed: Optional[int] = None,
        return_last_frame: bool = False,
    ) -> str:
        """
        Create video generation task

        Returns:
            Task ID
        """
        payload = {
            "model": model,
            "content": content,
            "duration": duration,
            "ratio": ratio,
            "resolution": resolution,
            "camera_fixed": camera_fixed,
            "watermark": watermark,
        }

        # Only include generate_audio if explicitly enabled (for 1.5 pro model)
        if generate_audio:
            payload["generate_audio"] = generate_audio

        if seed is not None:
            payload["seed"] = seed

        if return_last_frame:
            payload["return_last_frame"] = return_last_frame

        print_info("正在创建视频生成任务...")
        print_info(f"模型: {model}")
        print_info(f"时长: {duration}秒")
        print_info(f"比例: {ratio}")
        print_info(f"分辨率: {resolution}")
        print_info(f"生成音频: {generate_audio}")

        response = self._make_request("/contents/generations/tasks", payload)

        task_id = response.get("id")
        if not task_id:
            raise Exception(f"创建任务失败: {response}")

        print_success(f"任务创建成功: {task_id}")
        return task_id

    def get_task_status(self, task_id: str) -> Dict:
        """Get task status"""
        return self._make_request(f"/contents/generations/tasks/{task_id}", method="GET")

    def poll_task(self, task_id: str, return_last_frame: bool = False) -> str:
        """
        Poll task until completion

        Args:
            task_id: Task ID
            return_last_frame: If True, returns "video_url|last_frame_url" format

        Returns:
            Video URL, or "video_url|last_frame_url" if return_last_frame=True
        """
        print_info(f"开始轮询任务状态 (任务ID: {task_id})")
        print_info("预计等待时间: 2-5 分钟...")

        start_time = time.time()

        while True:
            elapsed = int(time.time() - start_time)

            if elapsed > MAX_POLL_TIME:
                print_error(f"轮询超时（超过 {MAX_POLL_TIME} 秒）")
                print_info("任务可能仍在处理，您可以稍后手动查询:")
                print_info(f"  curl {self.base_url}/contents/generations/tasks/{task_id} \\")
                print_info(f'    -H "Authorization: Bearer ${{ARK_API_KEY}}"')
                raise TimeoutError("Polling timeout")

            response = self.get_task_status(task_id)
            status = response.get("status")

            if status == "succeeded":
                print_success("视频生成成功！")
                video_url = response.get("content", {}).get("video_url")
                last_frame_url = response.get("content", {}).get("last_frame_url")

                if not video_url:
                    raise Exception(f"无法提取视频 URL: {response}")

                if return_last_frame and last_frame_url:
                    return f"{video_url}|{last_frame_url}"
                return video_url

            elif status == "failed":
                print_error("视频生成失败")
                error_msg = response.get("message", "未知错误")
                print_error(f"错误信息: {error_msg}")
                raise Exception(f"Task failed: {error_msg}")

            elif status == "queued":
                print_progress(f"[{elapsed}s] 任务排队中...")

            elif status == "running":
                print_progress(f"[{elapsed}s] 视频生成中...")

            else:
                print_progress(f"[{elapsed}s] 未知状态: {status}")

            time.sleep(POLL_INTERVAL)

    def download_video(self, video_url: str, output_path: str) -> str:
        """
        Download video from URL

        Returns:
            Path to downloaded file
        """
        print_info(f"正在下载视频...")
        print_info(f"URL: {video_url}")

        req = urllib.request.Request(video_url, headers={"User-Agent": "Mozilla/5.0"})

        with urllib.request.urlopen(req, timeout=120) as response:
            with open(output_path, "wb") as f:
                f.write(response.read())

        # Get file size
        from pathlib import Path
        file_size = Path(output_path).stat().st_size
        file_size_mb = file_size / (1024 * 1024)

        print_success(f"视频下载成功！")
        print_success(f"文件: {output_path}")
        print_success(f"大小: {file_size_mb:.2f} MB")

        return output_path
