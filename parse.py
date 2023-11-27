from pycparser import c_ast, parse_file, c_generator
import copy

class FuncDefVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.array_decls = []

    def visit_Decl(self, node):
        if isinstance(node.type, c_ast.ArrayDecl) and node.name == 'A':
            shadow_names = ['Aw', 'Ar', 'Anp', 'Anx']
            array_size = node.type.dim.value

            for name in shadow_names:
                array_type = c_ast.ArrayDecl(type=c_ast.TypeDecl(declname=name, quals=[], align=None, type=c_ast.IdentifierType(names=['int'])), dim=c_ast.Constant(type='int', value=array_size), dim_quals=[])
                init_list = c_ast.InitList([c_ast.Constant(type='int', value='0') for _ in range(int(array_size))])

                array_decl = c_ast.Decl(name=name, quals=[], storage=[], funcspec=[], type=array_type, bitsize=None, init=init_list, align=None)
                
                self.array_decls.append(array_decl)

class LoopVisitor(c_ast.NodeVisitor):
    def visit_For(self, node):
        # print(node.stmt.block_items)
        updated_node = copy.deepcopy(node.stmt.block_items)

        for i, stmt in enumerate(node.stmt.block_items):
            if isinstance(stmt, c_ast.Decl) and isinstance(stmt.init, c_ast.ArrayRef) and stmt.init.name.name == 'A':
                updated_node.insert(i + 1, mark_read_and_priv(stmt.init.subscript))
            
            elif isinstance(stmt, c_ast.Assignment):
                if isinstance(stmt.rvalue, c_ast.BinaryOp):
                    subscr = None
                    if isinstance(stmt.rvalue.left, c_ast.ArrayRef) and stmt.rvalue.left.name.name == 'A':
                        subscr = stmt.rvalue.left.subscript
                    elif isinstance(stmt.rvalue.right, c_ast.ArrayRef) and stmt.rvalue.right.name.name == 'A':
                        subscr = stmt.rvalue.right.subscript
                    
                    if subscr is not None:
                        updated_node.insert(i + 1, mark_read_and_priv(stmt.init.subscript))
            
            elif isinstance(stmt, c_ast.If):
                if isinstance(stmt.cond, c_ast.BinaryOp):
                    subscr = None
                    if isinstance(stmt.cond.left, c_ast.ArrayRef) and stmt.cond.left.name.name == 'A':
                        subscr = stmt.left.subscript
                    if isinstance(stmt.cond.right, c_ast.ArrayRef) and stmt.cond.right.name.name == 'A':
                        subscr = stmt.right.subscript
                                
                for j, ops in enumerate(stmt.iftrue.block_items):
                    print(ops)

def mark_read_and_priv(subscr):
    Aw_ref_check = c_ast.ArrayRef(name=c_ast.ID(name='Aw'), subscript=subscr)
    condition = c_ast.BinaryOp(op='==', left=Aw_ref_check, right=c_ast.Constant(type='int', value='0'))
    mark_Ar = c_ast.Assignment(op='=', lvalue = c_ast.ArrayRef(name=c_ast.ID(name='Ar'), subscript=subscr), rvalue=c_ast.Constant(type='int', value='1'))
    mark_Anp = c_ast.Assignment(op='=', lvalue = c_ast.ArrayRef(name=c_ast.ID(name='Anp'), subscript=subscr), rvalue=c_ast.Constant(type='int', value='1'))
    iftrue_stmts = c_ast.Compound(block_items=[mark_Ar, mark_Anp])
    written_check = c_ast.If(cond=condition, iftrue=iftrue_stmts, iffalse=None)

    return written_check

                    
def shadow_array(filename):
    ast = parse_file(filename)

    v = FuncDefVisitor()
    v.visit(ast)

    # print(ast.ext)

    for i, decl in enumerate(ast.ext[0].body.block_items):
        if decl.name == 'A':
            stop = i
            break
    
    ast.ext[0].body.block_items = ast.ext[0].body.block_items[0:stop+1] + v.array_decls + ast.ext[0].body.block_items[stop+1:]

    loop = LoopVisitor()
    loop.visit(ast)

    generator = c_generator.CGenerator()
    modified_code = generator.visit(ast)

    # print(modified_code)

filename = 'example.c'
shadow_array(filename)