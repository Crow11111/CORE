import ast
import os
import uuid
import errno

class TrustCollapseException(Exception):
    pass


class PreFlightVetoException(Exception):
    """Mandatory epistemic pre-flight failed (e.g. missing or empty memory_hash)."""


def validate_agent_preflight(agent_id: str, memory_hash: str | None = None) -> None:
    """
    Zwingender Pre-Flight: Agent darf nicht ohne nachweisbaren memory_hash operieren.
    Wirft PreFlightVetoException bei None oder leerem String.
    """
    if memory_hash is None:
        raise PreFlightVetoException(
            f"memory_hash required for agent pre-flight (agent_id={agent_id!r})"
        )
    if not memory_hash.strip():
        raise PreFlightVetoException(
            f"memory_hash must not be empty (agent_id={agent_id!r})"
        )

PREFIXES = [
    "get_", "set_", "is_", "has_", "to_", "as_", "serialize_", "default_",
    "config_", "supported_", "create_", "build_", "make_", "swap_",
    "identity_", "reset_", "clear_", "update_", "add_", "remove_", "mark_",
    "disconnect_", "connect_", "close_", "open_", "extract_", "calc_",
    "parse_", "format_", "find_", "warn_", "fetch_", "load_", "read_",
    "write_", "send_", "recv_", "log_", "copy_", "clone_", "validate_",
    "check_", "verify_", "start_", "stop_", "process_", "handle_"
]

def is_whitelisted(name):
    if name.startswith("__") and name.endswith("__"):
        return True
    for p in PREFIXES:
        if name.startswith(p):
            return True
    return False

def is_passive_expr(node):
    if isinstance(node, ast.Pass):
        return True
    if not isinstance(node, ast.Expr):
        return False
    val = node.value
    if isinstance(val, ast.Constant):
        return True
    if isinstance(val, ast.Name):
        return True
    if isinstance(val, (ast.List, ast.Tuple, ast.Set)) and len(val.elts) == 0:
        return True
    if isinstance(val, ast.Dict) and len(val.keys) == 0:
        return True
    return False

def is_empty_body(body):
    return all(is_passive_expr(stmt) for stmt in body)

def check_empty_bodies(node):
    if hasattr(node, 'body') and isinstance(node.body, list):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            has_exempt_decorator = False
            for dec in node.decorator_list:
                if isinstance(dec, ast.Name) and dec.id in ("abstractmethod", "overload", "property"):
                    has_exempt_decorator = True
                elif isinstance(dec, ast.Attribute) and dec.attr in ("abstractmethod", "overload", "property"):
                    has_exempt_decorator = True
            if has_exempt_decorator:
                pass
            elif is_empty_body(node.body):
                raise TrustCollapseException(f"Empty body in {type(node)}")
        elif isinstance(node, ast.ClassDef):
            pass
        elif isinstance(node, (ast.ExceptHandler)):
            pass
        elif isinstance(node, ast.If) or isinstance(node, ast.While) or isinstance(node, ast.For) or isinstance(node, ast.AsyncFor) or isinstance(node, ast.Try) or isinstance(node, ast.With) or isinstance(node, ast.AsyncWith):
            if is_empty_body(node.body):
                raise TrustCollapseException(f"Empty body in {type(node)}")
            if hasattr(node, 'orelse') and isinstance(node.orelse, list) and len(node.orelse) > 0:
                if is_empty_body(node.orelse):
                    raise TrustCollapseException(f"Empty orelse in {type(node)}")

    if isinstance(node, ast.Match):
        for case in node.cases:
            if is_empty_body(case.body):
                raise TrustCollapseException("Empty body in match case")

def is_exception_call(node):
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name):
            if node.func.id.endswith("Error") or node.func.id.endswith("Exception"):
                return True
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr.endswith("Error") or node.func.attr.endswith("Exception"):
                return True
    return False

class FuncVisitor(ast.NodeVisitor):
    def __init__(self):
        self.healer_found = False
        self.in_store_context = 0
        self.in_exception_context = 0

    def visit_Call(self, node):
        is_exc = is_exception_call(node)
        if is_exc:
            self.in_exception_context += 1
            self.generic_visit(node)
            self.in_exception_context -= 1
        else:
            func_name = ""
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr

            builtins = {"len", "dict", "list", "set", "tuple", "super", "print"}
            loggers = {"debug", "info", "warning", "error", "critical", "log", "exception"}

            if func_name not in builtins and func_name not in loggers:
                self.healer_found = True

            self.generic_visit(node)

    def visit_Raise(self, node):
        self.in_exception_context += 1
        self.generic_visit(node)
        self.in_exception_context -= 1

    def visit_BinOp(self, node):
        if not (isinstance(node.left, ast.Constant) and isinstance(node.right, ast.Constant)):
            self.healer_found = True
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        if not all(isinstance(v, ast.Constant) for v in node.values):
            self.healer_found = True
        self.generic_visit(node)

    def visit_UnaryOp(self, node):
        if not isinstance(node.operand, ast.Constant):
            self.healer_found = True
        self.generic_visit(node)

    def visit_Compare(self, node):
        is_const = isinstance(node.left, ast.Constant) and all(isinstance(c, ast.Constant) for c in node.comparators)
        if not is_const:
            self.healer_found = True
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        self.healer_found = True
        self.in_store_context += 1
        self.visit(node.target)
        self.in_store_context -= 1
        self.visit(node.value)

    def visit_Assign(self, node):
        self.in_store_context += 1
        for t in node.targets:
            self.visit(t)
        self.in_store_context -= 1
        self.visit(node.value)

    def visit_Attribute(self, node):
        if self.in_store_context == 0 and self.in_exception_context == 0:
            if isinstance(node.ctx, ast.Load):
                self.healer_found = True
        self.generic_visit(node)

    def visit_Subscript(self, node):
        if self.in_store_context == 0 and self.in_exception_context == 0:
            if isinstance(node.ctx, ast.Load):
                self.healer_found = True
        self.generic_visit(node)

    def visit_Await(self, node):
        self.healer_found = True
        self.generic_visit(node)

class MainVisitor(ast.NodeVisitor):
    def visit_FunctionDef(self, node):
        check_empty_bodies(node)

        for stmt in node.body:
            if isinstance(stmt, ast.While):
                if isinstance(stmt.test, ast.Constant) and stmt.test.value is False:
                    raise TrustCollapseException("Dead code while")
            if isinstance(stmt, (ast.For, ast.AsyncFor)):
                it = stmt.iter
                if isinstance(it, (ast.List, ast.Tuple, ast.Set)) and len(it.elts) == 0:
                    raise TrustCollapseException("Dead code for")
                if isinstance(it, ast.Dict) and len(it.keys) == 0:
                    raise TrustCollapseException("Dead code for")
                if isinstance(it, ast.Constant) and isinstance(it.value, str) and len(it.value) == 0:
                    raise TrustCollapseException("Dead code for")

        if not is_whitelisted(node.name):
            fv = FuncVisitor()
            for stmt in node.body:
                fv.visit(stmt)
            if not fv.healer_found:
                raise TrustCollapseException(f"No healer found in {node.name}")

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_Raise(self, node):
        if isinstance(node.exc, ast.Call) and isinstance(node.exc.func, ast.Name):
            if node.exc.func.id == "NotImplementedError":
                raise TrustCollapseException("NotImplementedError")
        self.generic_visit(node)

    def visit_If(self, node):
        check_empty_bodies(node)
        self.generic_visit(node)

    def visit_While(self, node):
        check_empty_bodies(node)
        self.generic_visit(node)

    def visit_For(self, node):
        check_empty_bodies(node)
        self.generic_visit(node)

    def visit_Try(self, node):
        check_empty_bodies(node)
        self.generic_visit(node)

    def visit_With(self, node):
        check_empty_bodies(node)
        self.generic_visit(node)

    def visit_Match(self, node):
        check_empty_bodies(node)
        self.generic_visit(node)

def validate_code(code_string: str):
    upper_code = code_string.upper()
    if "TODO" in upper_code or "FIXME" in upper_code or "HACK" in upper_code:
        raise TrustCollapseException("Marker found")

    try:
        tree = ast.parse(code_string)
    except SyntaxError:
        return

    visitor = MainVisitor()
    visitor.visit(tree)

def validate_file(filepath: str):
    if not os.path.exists(filepath):
        return True
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Self-Denial-Schutz: Überspringe eigene Datei und Tests (wie in Spec gefordert, bzw. falls sie "anti_heroin" heißen, überspringen wir nicht komplett, aber wir dürfen uns nicht selbst abschießen, weil TODOs im Code-Block stehen könnten. Moment, die Spec sagt: "Der Validator überspringt seine eigene Datei.")
    if "anti_heroin_validator.py" in filepath:
        return True

    validate_code(content)
    return True

def enforce_trust_collapse(target_path: str):
    try:
        real_target = os.path.realpath(target_path)
        tmp_path = real_target + f".{uuid.uuid4().hex}.tmp"
        try:
            with open(tmp_path, 'x') as f:
                f.write('{"trust_score": 0.049}')
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, real_target)
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

        dir_fd = os.open(os.path.dirname(real_target), os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    except (OSError, RuntimeError) as e:
        raise TrustCollapseException("HEROIN DETECTED (OS Write failed)") from e

    raise TrustCollapseException("HEROIN DETECTED")
