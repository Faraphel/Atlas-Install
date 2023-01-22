from typing import Callable

from source.safe_eval import BetterSafeEvalError
from source.safe_eval.safe_eval import safe_eval, SafeEvalException


class Object1:
    value_int = 1000
    value_str = "test"
    value_list = [1, 2, 3, 4, 5]
    value_list_rec = [[1, 2], [3, 4]]

    def method(self, value): return value
    def __repr__(self): return "repr test"


class Object2:
    def method2(self, value): return value
    sub_obj = Object1()


def assertRaise(func: Callable, expected_errors: "type | tuple[type]"):
    try:
        func()
        assert False
    except Exception as exc:
        assert isinstance(exc, expected_errors)


def test_arithmetic():
    assert safe_eval("1 + 5 * 7 ** 2")() == 1 + 5 * 7 ** 2


def test_list():
    assert safe_eval("['string', 10, 0x189, [], (), {}]")() == ['string', 10, 0x189, [], (), {}]


def test_slicing():
    assert safe_eval("[1, 2, 3, 4, 5][2]")() == 3


def test_dict():
    assert safe_eval("{'a': 1, 'b': 2, 'c': 3}['a']")() == 1


def test_builtins_method():
    assert safe_eval("','.join(['a', 'b', 'c'])")() == "a,b,c"


def test_import():
    assertRaise(lambda: safe_eval("import os")(), SafeEvalException)


def test_import_dunder():
    assertRaise(lambda: safe_eval("__import__('os')")(), SafeEvalException)


def test_non_lambda_expression():
    assertRaise(lambda: safe_eval("x = 100")(), SafeEvalException)


def test_dunder():
    assertRaise(lambda: safe_eval("().__class__.__bases__")(), SafeEvalException)


def test_getattr_env():
    assert safe_eval("obj.value_int", env={"obj": Object1()})() == 1000


def test_getvalue_env():
    assert safe_eval("value", env={"value": 1000})() == 1000


def test_setvalue_env():
    assertRaise(lambda: safe_eval("(value := 100)", env={"value": 1000})(), SafeEvalException)


def test_getattr_arg():
    assert safe_eval("obj.value_int", args=["obj"])(obj=Object1()) == 1000


def test_getvalue_arg():
    assert safe_eval("value", args=["value"])(value=1000) == 1000


def test_setvalue_arg():
    assertRaise(lambda: safe_eval("(value := 100)", args=["value"])(value=1000), SafeEvalException)


def test_assign():
    assert safe_eval("(value := 100)")() == 100


def test_assign_copy_value():
    obj = Object1()
    safe_eval("(value := obj.value_list_rec[0], value := [100])", env={"obj": obj})()
    assert obj.value_list_rec[0] == [1, 2]


def test_assign_copy_func():
    assertRaise(lambda: safe_eval("(value := func)", env={"func": lambda: 'pass'})(), BetterSafeEvalError)


def test_assign_copy_method():
    assertRaise(lambda: safe_eval("(value := obj.method)", env={"obj": Object1()})(), BetterSafeEvalError)


def test_call_method():
    assertRaise(lambda: safe_eval("obj.method('test')", env={"obj": Object1()})(), SafeEvalException)


def test_getattr_value():
    assert safe_eval("getattr(obj, 'value_int')", env={"obj": Object1()})() == 1000


def test_getattr_value_dunder():
    assertRaise(lambda: safe_eval("getattr(obj, '__dict__')", env={"obj": Object1()})(), BetterSafeEvalError)


def test_getattr_method_dunder():
    assertRaise(lambda: safe_eval("getattr(obj, 'method')", env={"obj": Object1()})(), BetterSafeEvalError)


def test_call_submethod():
    assertRaise(lambda: safe_eval("obj.sub_obj.method('test')", env={"obj": Object2()})(), SafeEvalException)


def test_class_new():
    safe_eval("obj_class()", env={"obj_class": Object1})()


def test_raise():
    assertRaise(lambda: safe_eval("raise Exception()")(), SafeEvalException)


def test_assert():
    assertRaise(lambda: safe_eval("assert True")(), SafeEvalException)


def test_del():
    assertRaise(lambda: safe_eval("(x := 10, del x)")(), SyntaxError)


def test_import_from():
    assertRaise(lambda: safe_eval("from os import path")(), SafeEvalException)


def test_lambda():
    assertRaise(lambda: safe_eval("(lambda x: x ** 2)(10)")(), SafeEvalException)


def test_global():
    assertRaise(lambda: safe_eval("(x := 10, global x)")(), SyntaxError)


def test_nonlocal():
    assertRaise(lambda: safe_eval("(x := 10, nonlocal x)")(), SyntaxError)


def test_class_def():
    assertRaise(lambda: safe_eval("(class c: pass)")(), SyntaxError)


def test_list_comprehension():
    # could maybe be authorised ???
    assertRaise(lambda: safe_eval("[x for x in range(10)]")() == [x for x in range(10)], SafeEvalException)


def test_list_comprehension_override():
    assertRaise(lambda: safe_eval("[x for x in range(10)]", env={"x": "value"})(), SafeEvalException)


def test_list_comprehension_method():
    assertRaise(lambda: safe_eval("[x('test') for x in [obj.method]]", env={"obj": Object1()})(), SafeEvalException)


def test_list_slicing():
    assertRaise(lambda: safe_eval("[obj.method][0]('value')", env={"obj": Object1()})(), SafeEvalException)
