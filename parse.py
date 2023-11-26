from pycparser import c_ast, parse_file, c_generator

class FuncDefVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.array_decls = []

    def visit_Decl(self, node):
        if isinstance(node.type, c_ast.ArrayDecl) and node.name == 'A':
            array_size = node.type.dim.value
            array_type = c_ast.ArrayDecl(type=c_ast.TypeDecl(declname='A_copy', quals=[], align=None, type=c_ast.IdentifierType(names=['int'])), dim=c_ast.Constant(type='int', value=array_size), dim_quals=[])
            init_list = c_ast.InitList([c_ast.Constant(type='int', value='0') for _ in range(int(array_size))])

            array_decl = c_ast.Decl(name='A_copy', quals=[], storage=[], funcspec=[], type=array_type, bitsize=None, init=init_list, align=None)
            
            self.array_decls.append(array_decl)
            
def shadow_array(filename):
    ast = parse_file(filename)

    v = FuncDefVisitor()
    v.visit(ast)

    ast.ext.extend(v.array_decls)

    # Generate the modified C code
    generator = c_generator.CGenerator()
    modified_code = generator.visit(ast)
    print(modified_code)


filename = 'example.c'

shadow_array(filename)