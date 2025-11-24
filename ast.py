from dataclasses import dataclass
from typing import List, Optional, Tuple, Any

class Node: pass

@dataclass
class Program(Node):
    decls: List[Node]

@dataclass
class VarDecl(Node):
    type: str
    name: str

@dataclass
class FuncDecl(Node):
    ret_type: str
    name: str
    params: List['Param']
    body: 'CompoundStmt'

@dataclass
class Param(Node):
    type: str
    name: str

@dataclass
class CompoundStmt(Node):
    local_decls: List[VarDecl]
    stmts: List[Node]

@dataclass
class IfStmt(Node):
    cond: Node
    then_stmt: Node
    else_stmt: Optional[Node]

@dataclass
class WhileStmt(Node):
    cond: Node
    body: Node

@dataclass
class ReturnStmt(Node):
    expr: Optional[Node]

@dataclass
class ExprStmt(Node):
    expr: Optional[Node]

@dataclass
class Assignment(Node):
    name: str
    expr: Node

@dataclass
class BinaryOp(Node):
    op: str
    left: Node
    right: Node

@dataclass
class UnaryOp(Node):
    op: str
    operand: Node

@dataclass
class Call(Node):
    name: str
    args: List[Node]

@dataclass
class Identifier(Node):
    name: str

@dataclass
class IntLiteral(Node):
    value: int

class Symbol:
    def __init__(self, name, kind, type_, scope_level, params=None):
        self.name = name
        self.kind = kind
        self.type = type_
        self.scope_level = scope_level
        self.params = params or []

class SymbolTable:
    def __init__(self):
        self.scopes = [{}]  
        self.level = 0

    def push(self):
        self.level += 1
        self.scopes.append({})

    def pop(self):
        self.scopes.pop()
        self.level -= 1

    def declare(self, symbol: Symbol):
        self.scopes[-1][symbol.name] = symbol

    def lookup(self, name: str) -> Optional[Symbol]:
        for s in reversed(self.scopes):
            if name in s:
                return s[name]
        return None

class TACGenerator:
    def __init__(self):
        self.temp_counter = 0
        self.label_counter = 0
        self.code = []  
        self.symtab = SymbolTable()

    def new_temp(self):
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def new_label(self):
        self.label_counter += 1
        return f"L{self.label_counter}"

    def emit(self, instr: str):
        self.code.append(instr)

    def generate(self, node: Node):
        if isinstance(node, Program):
            for d in node.decls:
                self.generate(d)
        elif isinstance(node, FuncDecl):
            self.emit(f"func {node.name}:")
            self.symtab.push()
            for p in node.params:
                self.symtab.declare(Symbol(p.name, 'param', p.type, self.symtab.level))
            for ld in node.body.local_decls:
                self.symtab.declare(Symbol(ld.name, 'var', ld.type, self.symtab.level))
            for s in node.body.stmts:
                self.gen_stmt(s)
            self.emit(f"endfunc {node.name}")
            self.symtab.pop()
        elif isinstance(node, VarDecl):
            self.symtab.declare(Symbol(node.name, 'var', node.type, self.symtab.level))
        else:
            raise NotImplementedError(type(node))

    def gen_stmt(self, stmt: Node):
        if isinstance(stmt, ExprStmt):
            if stmt.expr:
                self.gen_expr(stmt.expr)
        elif isinstance(stmt, CompoundStmt):
            self.symtab.push()
            for ld in stmt.local_decls:
                self.symtab.declare(Symbol(ld.name, 'var', ld.type, self.symtab.level))
            for s in stmt.stmts:
                self.gen_stmt(s)
            self.symtab.pop()
        elif isinstance(stmt, IfStmt):
            else_label = self.new_label()
            end_label = self.new_label()
            cond_place = self.gen_expr(stmt.cond)
            self.emit(f"ifFalse {cond_place} goto {else_label}")
            self.gen_stmt(stmt.then_stmt)
            self.emit(f"goto {end_label}")
            self.emit(f"{else_label}:")
            if stmt.else_stmt:
                self.gen_stmt(stmt.else_stmt)
            self.emit(f"{end_label}:")
        elif isinstance(stmt, WhileStmt):
            start = self.new_label()
            end = self.new_label()
            self.emit(f"{start}:")
            cond_place = self.gen_expr(stmt.cond)
            self.emit(f"ifFalse {cond_place} goto {end}")
            self.gen_stmt(stmt.body)
            self.emit(f"goto {start}")
            self.emit(f"{end}:")
        elif isinstance(stmt, ReturnStmt):
            if stmt.expr:
                r = self.gen_expr(stmt.expr)
                self.emit(f"return {r}")
            else:
                self.emit("return")
        elif isinstance(stmt, Assignment):
            r = self.gen_expr(stmt.expr)
            sym = self.symtab.lookup(stmt.name)
            if not sym:
                self.symtab.declare(Symbol(stmt.name, 'var', 'int', self.symtab.level))
            self.emit(f"{stmt.name} = {r}")
        else:
            raise NotImplementedError(type(stmt))

    def gen_expr(self, expr: Node) -> str:
        if isinstance(expr, IntLiteral):
            t = self.new_temp()
            self.emit(f"{t} = {expr.value}")
            return t
        elif isinstance(expr, Identifier):
            sym = self.symtab.lookup(expr.name)
            if sym:
                return expr.name
            else:
                return expr.name
        elif isinstance(expr, BinaryOp):
            l = self.gen_expr(expr.left)
            r = self.gen_expr(expr.right)
            t = self.new_temp()
            self.emit(f"{t} = {l} {expr.op} {r}")
            return t
        elif isinstance(expr, UnaryOp):
            o = self.gen_expr(expr.operand)
            t = self.new_temp()
            self.emit(f"{t} = {expr.op}{o}")
            return t
        elif isinstance(expr, Assignment):
            r = self.gen_expr(expr.expr)
            self.emit(f"{expr.name} = {r}")
            return expr.name
        elif isinstance(expr, Call):
            arg_places = []
            for a in expr.args:
                arg_places.append(self.gen_expr(a))
            for ap in arg_places:
                self.emit(f"param {ap}")
            ret = self.new_temp()
            self.emit(f"{ret} = call {expr.name}, {len(arg_places)}")
            return ret
        else:
            raise NotImplementedError(type(expr))

if __name__ == "__main__":
    ast = Program(decls=[
        FuncDecl(
            ret_type='int',
            name='main',
            params=[],
            body=CompoundStmt(
                local_decls=[VarDecl('int', 'a')],
                stmts=[
                    ExprStmt(Assignment('a', BinaryOp('+', IntLiteral(2), BinaryOp('*', IntLiteral(3), IntLiteral(4))))),
                    ReturnStmt(Identifier('a'))
                ]
            )
        )
    ])

    gen = TACGenerator()
    gen.generate(ast)
    print("\n".join(gen.code))
