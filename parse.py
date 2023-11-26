from pycparser import c_ast, parse_file, c_generator

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
            
def shadow_array(filename):
    ast = parse_file(filename)

    v = FuncDefVisitor()
    v.visit(ast)

    for i, decl in enumerate(ast.ext[0].body.block_items):
        if decl.name == 'A':
            stop = i
            break
    
    ast.ext[0].body.block_items = ast.ext[0].body.block_items[0:stop+1] + v.array_decls + ast.ext[0].body.block_items[stop+1:]

    # Generate the modified C code
    generator = c_generator.CGenerator()
    modified_code = generator.visit(ast)
    print(modified_code)


filename = 'example.c'

shadow_array(filename)