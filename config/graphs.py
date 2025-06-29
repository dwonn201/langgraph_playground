import random
from IPython.display import Image, display
from langgraph.graph.state import CompiledStateGraph
from dataclasses import dataclass
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

@dataclass
class NodeStyles:
    default: str = (
        "fill:#45C4B0, fill-opacity:0.3, color:#23260F, stroke:#45C4B0, stroke-width:1px, font-weight:bold, line-height:1.2"  # 기본 색상
    )
    first: str = (
        "fill:#45C4B0, fill-opacity:0.1, color:#23260F, stroke:#45C4B0, stroke-width:1px, font-weight:normal, font-style:italic, stroke-dasharray:2,2"  # 점선 테두리
    )
    last: str = (
        "fill:#45C4B0, fill-opacity:1, color:#000000, stroke:#45C4B0, stroke-width:1px, font-weight:normal, font-style:italic, stroke-dasharray:2,2"  # 점선 테두리
    )

def visualize_graph(graph, xray=False):
    """
    CompiledStateGraph 객체를 시각화하여 표시합니다.

    이 함수는 주어진 그래프 객체가 CompiledStateGraph 인스턴스인 경우
    해당 그래프를 Mermaid 형식의 PNG 이미지로 변환하여 표시합니다.

    Args:
        graph: 시각화할 그래프 객체. CompiledStateGraph 인스턴스여야 합니다.

    Returns:
        None

    Raises:
        Exception: 그래프 시각화 과정에서 오류가 발생한 경우 예외를 출력합니다.
    """
    try:
        # 그래프 시각화
        if isinstance(graph, CompiledStateGraph):
            display(
                Image(
                    graph.get_graph(xray=xray).draw_mermaid_png(
                        background_color="white",
                        node_colors=NodeStyles(),
                    )
                )
            )
    except Exception as e:
        print(f"[ERROR] Visualize Graph Error: {e}")


# 각 깊이 수준에 대해 미리 정의된 색상 (ANSI 이스케이프 코드 사용)
depth_colors = {
    1: "\033[96m",  # 밝은 청록색 (눈에 잘 띄는 첫 계층)
    2: "\033[93m",  # 노란색 (두 번째 계층)
    3: "\033[94m",  # 밝은 초록색 (세 번째 계층)
    4: "\033[95m",  # 보라색 (네 번째 계층)
    5: "\033[92m",  # 밝은 파란색 (다섯 번째 계층)
    "default": "\033[96m",  # 기본값은 밝은 청록색으로
    "reset": "\033[0m",  # 기본 색상으로 재설정
}


def is_terminal_dict(data):
    """말단 딕셔너리인지 확인합니다."""
    if not isinstance(data, dict):
        return False
    for value in data.values():
        if isinstance(value, (dict, list)) or hasattr(value, "__dict__"):
            return False
    return True


def format_terminal_dict(data):
    """말단 딕셔너리를 포맷팅합니다."""
    items = []
    for key, value in data.items():
        if isinstance(value, str):
            items.append(f'"{key}": "{value}"')
        else:
            items.append(f'"{key}": {value}')
    return "{" + ", ".join(items) + "}"


def _display_message_tree(data, indent=0, node=None, is_root=False):
    """
    JSON 객체의 트리 구조를 타입 정보 없이 출력합니다.
    """
    spacing = " " * indent * 4
    color = depth_colors.get(indent + 1, depth_colors["default"])

    if isinstance(data, dict):
        if not is_root and node is not None:
            if is_terminal_dict(data):
                print(
                    f'{spacing}{color}{node}{depth_colors["reset"]}: {format_terminal_dict(data)}'
                )
            else:
                print(f'{spacing}{color}{node}{depth_colors["reset"]}:')
                for key, value in data.items():
                    _display_message_tree(value, indent + 1, key)
        else:
            for key, value in data.items():
                _display_message_tree(value, indent + 1, key)

    elif isinstance(data, list):
        if not is_root and node is not None:
            print(f'{spacing}{color}{node}{depth_colors["reset"]}:')

        for index, item in enumerate(data):
            print(f'{spacing}    {color}index [{index}]{depth_colors["reset"]}')
            _display_message_tree(item, indent + 1)

    elif hasattr(data, "__dict__") and not is_root:
        if node is not None:
            print(f'{spacing}{color}{node}{depth_colors["reset"]}:')
        _display_message_tree(data.__dict__, indent)

    else:
        if node is not None:
            if isinstance(data, str):
                value_str = f'"{data}"'
            else:
                value_str = str(data)

            print(f'{spacing}{color}{node}{depth_colors["reset"]}: {value_str}')


def display_message_tree(message):
    """
    메시지 트리를 표시하는 주 함수입니다.
    """
    if isinstance(message, BaseMessage):
        _display_message_tree(message.__dict__, is_root=True)
    else:
        _display_message_tree(message, is_root=True)