import inspect
import importlib
from typing import Any, Callable, List, Tuple, Dict, Union


def get_object_name(obj: Any) -> str:
    """オブジェクトの名前を取得する"""
    return getattr(obj, "__name__", type(obj).__name__)


def get_class(class_name: str, module_name: str) -> Any:
    """指定されたモジュールからクラスオブジェクトを取得する"""
    try:
        module = importlib.import_module(module_name)
        return getattr(module, class_name)
    except (ImportError, AttributeError):
        return None


def display_inheritance_hierarchy(
    cls: type, indent: int = 0, visited: set = None
) -> None:
    """クラスの継承階層を再帰的に表示する"""
    if visited is None:
        visited = set()

    if cls in visited:
        print("  " * indent + f"- {cls.__name__} (循環参照)")
        return

    visited.add(cls)
    print("  " * indent + f"- {cls.__name__}")

    for base_class in cls.__bases__:
        if base_class.__name__ != "object":
            display_inheritance_hierarchy(base_class, indent + 1, visited)


def get_class_details(cls: type) -> Dict[str, Dict[str, List[Tuple[str, Any]]]]:
    """クラスのメソッドと属性を継承と独自に分類して取得する"""
    inherited = {"methods": [], "attributes": []}
    own = {"methods": [], "attributes": []}

    # 基底クラスのメソッドと属性を取得
    for base_class in cls.__bases__:
        if base_class.__name__ != "object":
            base_items = inspect.getmembers(base_class)
            for name, item in base_items:
                if inspect.ismethod(item) or inspect.isfunction(item):
                    inherited["methods"].append((name, item))
                else:
                    inherited["attributes"].append((name, item))

    # 現在のクラスのメソッドと属性を取得し、継承されたものと比較
    class_items = inspect.getmembers(cls)
    for name, item in class_items:
        if name.startswith("__") and name.endswith("__"):
            continue  # 特殊メソッドはスキップ
        if inspect.ismethod(item) or inspect.isfunction(item):
            if any(
                name == inherited_method[0] for inherited_method in inherited["methods"]
            ):
                own["methods"].append((name, item))  # オーバーライドされたメソッド
            else:
                own["methods"].append((name, item))  # 新規メソッド
        else:
            if any(
                name == inherited_attr[0] for inherited_attr in inherited["attributes"]
            ):
                own["attributes"].append((name, item))  # オーバーライドされた属性
            else:
                own["attributes"].append((name, item))  # 新規属性

    return {"inherited": inherited, "own": own}


def print_items(
    title: str,
    items: List[Tuple[str, Any]],
    condition: Callable[[str], bool] = lambda x: True,
) -> None:
    """項目のリストを条件に基づいてフィルタリングし、表示する"""
    filtered_items = [item for item in items if condition(item[0])]
    print(f"\n{title} 個数: {len(filtered_items)}")
    for name, item in filtered_items:
        if inspect.isfunction(item) or inspect.ismethod(item):
            signature = inspect.signature(item)
            print(f"  - {name}{signature}")
        else:
            print(f"  - {name}: {type(item).__name__}")


def inspect_library(library_name: str) -> None:
    """ライブラリの構造を分析し、主要なクラスのリストを表示する"""
    try:
        library = importlib.import_module(library_name)
        print(f"\n{'-'*40}")
        print(f"\n{library_name} ライブラリの分析\n")
        print(f"概要:\n{library.__doc__.strip() if library.__doc__ else '概要なし'}\n")

        classes = inspect.getmembers(library, inspect.isclass)
        print(f"クラスの数: {len(classes)}")
        print("\nクラスリスト:")
        for class_name, _ in classes:
            print(f"  - {class_name}")

    except ImportError:
        print(f"ライブラリ '{library_name}' をインポートできません。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")


def inspect_class(
    class_or_object: Union[str, type, Any], library_name: str = None
) -> None:
    """
    指定されたクラスまたはオブジェクトの詳細を分析して表示する

    :param class_or_object: クラス名（文字列）、クラスオブジェクト、または任意のオブジェクト
    :param library_name: クラス名が文字列で指定された場合に必要なライブラリ名（オプション）
    """
    if isinstance(class_or_object, str):
        if library_name is None:
            raise ValueError(
                "クラス名が文字列で指定された場合、library_nameも指定する必要があります。"
            )
        cls = get_class(class_or_object, library_name)
        if cls is None:
            print(
                f"クラス '{class_or_object}' は '{library_name}' 内に見つかりません。"
            )
            return
        class_name = class_or_object
    elif inspect.isclass(class_or_object):
        cls = class_or_object
        class_name = cls.__name__
    else:
        cls = type(class_or_object)
        class_name = cls.__name__

    print(f"\nクラス: {class_name}")
    print("継承階層:")
    display_inheritance_hierarchy(cls)

    class_details = get_class_details(cls)

    # 継承されたメソッドと属性の表示
    print("\n継承されたメソッドと属性:")
    print_items(
        "メソッド",
        class_details["inherited"]["methods"],
        lambda x: not x.startswith("_"),
    )
    print_items(
        "属性",
        class_details["inherited"]["attributes"],
        lambda x: not x.startswith("_"),
    )

    # 独自のメソッドと属性の表示
    print("\n独自のメソッドと属性:")
    print_items(
        "メソッド", class_details["own"]["methods"], lambda x: not x.startswith("_")
    )
    print_items(
        "属性", class_details["own"]["attributes"], lambda x: not x.startswith("_")
    )

    # クラスメソッドとスタティックメソッドの表示
    print_items(
        "クラスメソッド",
        class_details["own"]["methods"],
        lambda x: isinstance(cls.__dict__.get(x), classmethod),
    )
    print_items(
        "スタティックメソッド",
        class_details["own"]["methods"],
        lambda x: isinstance(cls.__dict__.get(x), staticmethod),
    )
