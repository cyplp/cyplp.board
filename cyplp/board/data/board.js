{
   "_id": "_design/board",
    "language": "javascript",
   "views": {
       "all": {
           "map": "function(doc) {\nif (doc.doc_type == 'Board')\n{\n  emit([doc.owner], doc);\n}\n}"
       },
       "content": {
           "map": "function(doc) {\n  if(doc.doc_type == 'Column')\n  {\n    emit([doc.board, 0], doc);\n  }\n if(doc.doc_type == 'Item')\n  {\n    emit([doc.board, 1], doc);\n  }\n if(doc.doc_type == 'TypeItem')\n  {\n    emit([doc.board, 2], doc);\n  }\n if(doc.doc_type == 'Tag')\n  {\n    emit([doc.board, 3], doc);\n  }\n\n}\n\n\n"
       },
       "config": {
           "map": "function(doc) {\n  \n if(doc.doc_type == 'TypeItem')\n  {\n    emit([doc.board, 0], doc);\n  }\n if(doc.doc_type == 'Tag')\n  {\n    emit([doc.board, 1], doc);\n  }\n}"
       }
   }
}
