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
            
            write_counter_decl = c_ast.Decl(name='write_counter', quals=[], align=[], storage=[], funcspec=[],
                                            type=c_ast.TypeDecl(declname='write_counter', quals=[], align=None, type=
                                                                c_ast.IdentifierType(names=['int'])), 
                                                                init=c_ast.Constant(type='int', value='0'), bitsize=None)
            
            distinct_write_counter_decl = c_ast.Decl(name='distinct_write_counter', quals=[], align=[], storage=[], funcspec=[],
                                            type=c_ast.TypeDecl(declname='distinct_write_counter', quals=[], align=None, type=
                                                                c_ast.IdentifierType(names=['int'])), 
                                                                init=c_ast.Constant(type='int', value='0'), bitsize=None)

            self.array_decls.append(write_counter_decl)
            self.array_decls.append(distinct_write_counter_decl)

class LoopVisitor(c_ast.NodeVisitor):
    def visit_For(self, node):
        write_increment = c_ast.Assignment(op='+=', lvalue=c_ast.ID(name='write_counter'), rvalue=c_ast.Constant(type='int', value='1'))
        updated_node = copy.deepcopy(node.stmt.block_items)
        last_insert_pt = -1

        for i, stmt in enumerate(node.stmt.block_items):
            if isinstance(stmt, c_ast.Decl) and isinstance(stmt.init, c_ast.ArrayRef) and stmt.init.name.name == 'A':
                if i > last_insert_pt:
                    updated_node.insert(i + 1, mark_read_and_priv(stmt.init.subscript))
                    updated_node.insert(i + 2, mark_nx(stmt.init.subscript))
                    last_insert_pt = i + 2
                else:
                    updated_node.insert(last_insert_pt + 1, mark_read_and_priv(stmt.init.subscript))
                    updated_node.insert(last_insert_pt + 2, mark_nx(stmt.init.subscript))
                    last_insert_pt += 2

            
            elif isinstance(stmt, c_ast.Assignment):
                if isinstance(stmt.rvalue, c_ast.BinaryOp):
                    subscr = None
                    mark_reduction = False
                    if isinstance(stmt.rvalue.left, c_ast.ArrayRef) and stmt.rvalue.left.name.name == 'A':
                        subscr = stmt.rvalue.left.subscript

                    elif isinstance(stmt.rvalue.right, c_ast.ArrayRef) and stmt.rvalue.right.name.name == 'A':
                        subscr = stmt.rvalue.right.subscript

                    # checking if reduction operation
                    if isinstance(stmt.lvalue, c_ast.ArrayRef) and stmt.lvalue.name.name == 'A':
                        if subscr.name != stmt.lvalue.subscript.name:
                            mark_reduction = True
                    
                    if subscr is not None:
                        if i > last_insert_pt:
                            updated_node.insert(i + 1, mark_read_and_priv(subscr))
                            if mark_reduction: updated_node.insert(i + 2, mark_nx(subscr))
                            last_insert_pt = i + 2
                        else:
                            updated_node.insert(last_insert_pt + 1, mark_read_and_priv(subscr))
                            if mark_reduction: updated_node.insert(last_insert_pt + 2, mark_nx(subscr))
                            last_insert_pt += 2

                        # updated_node.insert(i + 1, mark_read_and_priv(subscr))
                if isinstance(stmt.lvalue, c_ast.ArrayRef) and stmt.lvalue.name.name == 'A':
                    mark_Aw, mark_Awi, mark_Ar = mark_write(stmt.lvalue.subscript)
                    mark_reduction = False 

                    if isinstance(stmt.rvalue, c_ast.ArrayRef) and stmt.rvalue.name.name == 'A':
                        if stmt.lvalue.subscript.name != stmt.rvalue.subscript.name:
                            mark_reduction = True
                    
                    if i > last_insert_pt:
                        updated_node.insert(i + 1, mark_Aw)
                        updated_node.insert(i + 2, mark_Awi)
                        updated_node.insert(i + 3, mark_Ar)
                        updated_node.insert(i + 4, write_increment)
                        if mark_reduction: updated_node.insert(i + 5, mark_nx(stmt.lvalue.subscript))
                        last_insert_pt = i + 5
                    else:
                        updated_node.insert(last_insert_pt + 1, mark_Aw)
                        updated_node.insert(last_insert_pt + 2, mark_Awi)
                        updated_node.insert(last_insert_pt + 3, mark_Ar)
                        updated_node.insert(last_insert_pt + 4, write_increment)
                        if mark_reduction: updated_node.insert(last_insert_pt + 5, mark_nx(stmt.lvalue.subscript))
                        last_insert_pt = last_insert_pt + 5            
            
            elif isinstance(stmt, c_ast.If):
                if isinstance(stmt.cond, c_ast.BinaryOp):
                    # checking condition to branch or not contains array A
                    subscr = None

                    if isinstance(stmt.cond.left, c_ast.ArrayRef) and stmt.cond.left.name.name == 'A':
                        subscr = stmt.cond.left.subscript
                    if isinstance(stmt.cond.right, c_ast.ArrayRef) and stmt.cond.right.name.name == 'A':
                        subscr = stmt.cond.right.subscript
                    
                    if subscr is not None:
                        if i > last_insert_pt:
                            updated_node.insert(i + 1, mark_read_and_priv(subscr))
                            last_insert_pt = i + 1
                        else:
                            updated_node.insert(last_insert_pt + 1, mark_read_and_priv(subscr))
                            last_insert_pt += 1

                if_block_items = copy.deepcopy(stmt.iftrue.block_items)
                insert_idx = -1

                for j, new_stmt in enumerate(stmt.iftrue.block_items):
                    if isinstance(new_stmt, c_ast.Assignment):
                        if isinstance(new_stmt.rvalue, c_ast.BinaryOp):
                            subscr = None
                            mark_reduction = False

                            if isinstance(new_stmt.rvalue.left, c_ast.ArrayRef) and new_stmt.rvalue.left.name.name == 'A':
                                subscr = new_stmt.rvalue.left.subscript
                            elif isinstance(new_stmt.rvalue.right, c_ast.ArrayRef) and new_stmt.rvalue.right.name.name == 'A':
                                subscr = new_stmt.rvalue.right.subscript

                            if isinstance(new_stmt.lvalue, c_ast.ArrayRef) and new_stmt.lvalue.name.name == 'A' and subscr is not None:
                                if str(subscr) != str(new_stmt.lvalue.subscript):
                                    mark_reduction = True
                            
                            if subscr is not None:
                                if i > insert_idx:
                                    if_block_items.insert(i + 1, mark_read_and_priv(subscr))
                                    if mark_reduction: if_block_items.insert(i + 2, mark_nx(subscr))
                                    insert_idx = i + 2
                                else:
                                    if_block_items.insert(insert_idx + 1, mark_read_and_priv(subscr))
                                    if mark_reduction: if_block_items.insert(insert_idx + 2, mark_nx(subscr))
                                    insert_idx += 2

                        if isinstance(new_stmt.lvalue, c_ast.ArrayRef) and new_stmt.lvalue.name.name == 'A':
                            mark_Aw, mark_Awi, mark_Ar = mark_write(new_stmt.lvalue.subscript)
                            mark_reduction = False 

                            if isinstance(new_stmt.rvalue.left, c_ast.ArrayRef) and new_stmt.rvalue.left.name.name == 'A':
                                if str(new_stmt.lvalue.subscript) != str(new_stmt.rvalue.left.subscript):
                                    mark_reduction = True
                            elif not isinstance(new_stmt.rvalue, c_ast.ArrayRef):
                                mark_reduction = True

                            if i > insert_idx:
                                if_block_items.insert(i + 1, mark_Aw)
                                if_block_items.insert(i + 2, mark_Awi)
                                if_block_items.insert(i + 3, mark_Ar)
                                if_block_items.insert(i + 4, write_increment)
                                if mark_reduction: if_block_items.insert(i + 5, mark_nx(new_stmt.lvalue.subscript))
                                insert_idx = i + 5
                            else:
                                if_block_items.insert(insert_idx + 1, mark_Aw)
                                if_block_items.insert(insert_idx + 2, mark_Awi)
                                if_block_items.insert(insert_idx + 3, mark_Ar)
                                if_block_items.insert(insert_idx + 4, write_increment)
                                if mark_reduction: if_block_items.insert(i + 5, mark_nx(new_stmt.lvalue.subscript))
                                insert_idx = insert_idx + 5
                idx = 0
                for q in range(len(updated_node)):
                    if updated_node[q] == stmt:
                        idx = q
                        break
                
                updated_node[q].iftrue.block_items = if_block_items
                
        node.stmt.block_items = updated_node

        array_type = c_ast.ArrayDecl(type=c_ast.TypeDecl(declname='Awi', quals=[], align=None, type=c_ast.IdentifierType(names=['int'])), dim=c_ast.Constant(type='int', value='4'), dim_quals=[])
        init_list = c_ast.InitList([c_ast.Constant(type='int', value='0') for _ in range(int(4))])
        array_decl = c_ast.Decl(name='Awi', quals=[], storage=[], funcspec=[], type=array_type, bitsize=None, init=init_list, align=None)

        node.stmt.block_items.insert(0, array_decl)
                            
def mark_read_and_priv(subscr):
    Aw_ref_check = c_ast.ArrayRef(name=c_ast.ID(name='Awi'), subscript=subscr)
    condition = c_ast.BinaryOp(op='==', left=Aw_ref_check, right=c_ast.Constant(type='int', value='0'))
    mark_Ar = c_ast.Assignment(op='=', lvalue = c_ast.ArrayRef(name=c_ast.ID(name='Ar'), subscript=subscr), rvalue=c_ast.Constant(type='int', value='1'))
    mark_Anp = c_ast.Assignment(op='=', lvalue = c_ast.ArrayRef(name=c_ast.ID(name='Anp'), subscript=subscr), rvalue=c_ast.Constant(type='int', value='1'))
    iftrue_stmts = c_ast.Compound(block_items=[mark_Ar, mark_Anp])
    written_check = c_ast.If(cond=condition, iftrue=iftrue_stmts, iffalse=None)

    return written_check

def mark_write(subscr):
    mark_Aw = c_ast.Assignment(op='=', lvalue = c_ast.ArrayRef(name=c_ast.ID(name='Aw'), subscript=subscr), rvalue=c_ast.Constant(type='int', value='1'))
    mark_Awi = c_ast.Assignment(op='=', lvalue = c_ast.ArrayRef(name=c_ast.ID(name='Awi'), subscript=subscr), rvalue=c_ast.Constant(type='int', value='1'))
    mark_Ar = c_ast.Assignment(op='=', lvalue = c_ast.ArrayRef(name=c_ast.ID(name='Ar'), subscript=subscr), rvalue=c_ast.Constant(type='int', value='0'))

    return (mark_Aw, mark_Awi, mark_Ar)
    
def mark_nx(subscr):
    mark_Anx = c_ast.Assignment(op='=', lvalue = c_ast.ArrayRef(name=c_ast.ID(name='Anx'), subscript=subscr), rvalue=c_ast.Constant(type='int', value='1'))
    return mark_Anx

def count_distinct_writes():
    loop_body = c_ast.Compound([
        c_ast.If(
            cond=c_ast.BinaryOp(
                op='==',
                left=c_ast.ArrayRef(name=c_ast.ID(name='Aw'), subscript=c_ast.ID(name='i')),
                right=c_ast.Constant(type='int', value='1')
            ),
            iftrue=c_ast.Compound([
                c_ast.Assignment(
                    op='+=',
                    lvalue=c_ast.ID(name='distinct_write_counter'),
                    rvalue=c_ast.Constant(type='int', value='1')
                )
            ]),
            iffalse=None
        )
    ])

    loop = c_ast.For(
        init=c_ast.Decl(
            name='i',
            quals=[],
            storage=[],
            funcspec=[],
            align=None,
            type=c_ast.TypeDecl(
                declname='i',
                quals=[],
                type=c_ast.IdentifierType(names=['int']),
                align=None
            ),
            init=c_ast.Constant(type='int', value='0'),
            bitsize=None
        ),
        cond=c_ast.BinaryOp(
            op='<',
            left=c_ast.ID(name='i'),
            right=c_ast.Constant(type='int', value=str(4))
        ),
        next=c_ast.UnaryOp(
            op='++',
            expr=c_ast.ID(name='i')
        ),
        stmt=loop_body
    )

    return loop
    
    
def shadow_array(filename):
    ast = parse_file(filename)

    v = FuncDefVisitor()
    v.visit(ast)

    # print(ast.ext)

    for i, decl in enumerate(ast.ext[0].body.block_items):
        if decl.name == 'A':
            stop = i
            break
    
    end_loop = count_distinct_writes()
    
    ast.ext[0].body.block_items = ast.ext[0].body.block_items[0:stop+1] + v.array_decls + ast.ext[0].body.block_items[stop+1:]

    loop = LoopVisitor()
    loop.visit(ast)

    generator = c_generator.CGenerator()
    modified_code = generator.visit(ast)

    ast.ext[0].body.block_items = ast.ext[0].body.block_items + [end_loop]

    outfile = f'marked_examples/marked_{filename}'

    with open(outfile, 'w') as file:
        file.write(modified_code)

    # perform post processing, printing out Aw, Ar, Anp, Anx arrays, write_counter, distinct_write_counter
    # Read the existing content of the C file
    with open(outfile, 'r') as file:
        c_code = file.read()

    # Add the provided for loop before the "return 0;"
    printed_code = c_code.replace('return 0;', '''
    for (int i = 0; i < 4; ++i){
        if (Aw[i] == 1)
        ++distinct_write_counter;
    }

    for (int i = 0; i < 4; i++) {
        printf("%d ", Aw[i]);
    }
    printf("\\n");

    for (int i = 0; i < 4; i++) {
        printf("%d ", Ar[i]);
    }
    printf("\\n");

    for (int i = 0; i < 4; i++) {
        printf("%d ", Anx[i]);
    }
    printf("\\n");

    for (int i = 0; i < 4; i++) {
        printf("%d ", Anp[i]);
    }
    printf("\\n");
    
    printf("%d ", write_counter);
    printf("\\n");
    printf("%d ", distinct_write_counter);

    return 0;
    ''')

    # Write the modified content back to the file
    with open(outfile, 'w') as file:
        file.write(printed_code)

filename = 'example.c'
shadow_array(filename)