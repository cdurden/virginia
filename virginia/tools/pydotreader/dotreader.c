/*
    dotpipeR: R package for computational pipelines using the DOT grammar
    Copyright (C) 2013  Christopher L Durden <cdurden@gmail.com>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
*/

#include <stdio.h>
#include <math.h>
#include <string.h>

#include "graph.h"
#include "list.h"
#include "set.h"
#include "gdi.h"

#include "Python.h"

extern int parse_graph(GraphDataInterface *gdi);

FILE *fh;

static PyObject* readdot (PyObject* self, PyObject* args) {
  const char* file;
  if (!PyArg_ParseTuple(args, "s", &file))
        return NULL;

//  if(!isString(fn) || length(fn) != 1)
//    error("filename is not a single string");
//
//  const char *file = CHAR(STRING_ELT(fn, 0));
  int maxbytes = 65536;

//  SEXP nodes;
//  SEXP node_attrs;
//  SEXP edge_attrs;
//  SEXP preprocessor_lines;
////  SEXP graphdata;
//  SEXP attrs,attr;
//  SEXP edgemat;
//  SEXP dim;

  PyObject *graphdata;
  PyObject *preprocessor_lines;
  PyObject *nodes;
  PyObject *node_attrs;
  PyObject *attrs,*attr;
  PyObject *edgemat;
  PyObject *edge_attrs;
  
  List *edges;

  Graph graph;
  Vertex *vertex;
  Edge *edge;
//  Attr *index_attr;
//  char *index = "index";
  char *buf;
  int i,j; // node index
  GraphDataInterface gdi;
  graph_init(&graph);
  gdi_init(&gdi, &graph);

  if((fh = fopen(file,"r"))==NULL) {
//        printf("Cannot open file.\n");
    Py_RETURN_NONE;
//        return R_NilValue;
  }
        printf("processing dot data.\n");
  parse_graph(&gdi); // call function defined in yacc code
        printf("processing dot data.\n");
  if(!gdi.complete) {
    Py_RETURN_NONE;
//    return(R_NilValue);
  }

  if((buf = malloc(maxbytes*sizeof(char)))==NULL) {
//    printf("could not allocate character vector of length maxbytes=%d>0",maxbytes);
    Py_RETURN_NONE;
//    return R_NilValue;
  }

  // generate R objects to store vertex information 
//  PROTECT(graphdata = allocVector(VECSXP,5));
  graphdata = PyList_New(5);
  nodes = PyList_New(list_size(graph.vertices));
  node_attrs = PyList_New(list_size(graph.vertices));
  preprocessor_lines = PyList_New(list_size(gdi.preprocessor_lines));
//  PROTECT(nodes = allocVector(STRSXP,list_size(graph.vertices)));
//  PROTECT(node_attrs = allocVector(VECSXP,list_size(graph.vertices)));
//  PROTECT(preprocessor_lines = allocVector(STRSXP,list_size(gdi.preprocessor_lines)));

  ListElmt *vertex_elmt,*attr_elmt,*edge_elmt,*preprocessor_line_elmt;
  i=0;
  for (preprocessor_line_elmt = list_head(gdi.preprocessor_lines); preprocessor_line_elmt != NULL; preprocessor_line_elmt = list_next(preprocessor_line_elmt)) {
    buf = (char *)list_data(preprocessor_line_elmt);
    PyList_SetItem(preprocessor_lines, i++, PyUnicode_FromString(buf));
//    SET_STRING_ELT(preprocessor_lines, i++, mkChar(buf));
  }

  i=0;
  for (vertex_elmt = list_head(graph.vertices); vertex_elmt != NULL; vertex_elmt = list_next(vertex_elmt)) {
    vertex = (Vertex *)list_data(vertex_elmt);
    PyList_SetItem(nodes, i++, PyUnicode_FromString(vertex->id));
//    SET_STRING_ELT(nodes, i++, mkChar(vertex->id));
  }

  i=0;
  for (vertex_elmt = list_head(graph.vertices); vertex_elmt != NULL; vertex_elmt = list_next(vertex_elmt)) {

    vertex = (Vertex *)list_data(vertex_elmt);
    PyList_SetItem(nodes, i, PyUnicode_FromString(vertex->id));

//    SET_VECTOR_ELT(node_attrs,i, allocVector( VECSXP,list_size((List *)(vertex->data)) ));
//    attrs = VECTOR_ELT(node_attrs,i);

    
    attrs = PyList_New(list_size((List *)(vertex->data)));
    j=0;
    for (attr_elmt = list_head((List *)(vertex->data)); attr_elmt != NULL; attr_elmt = list_next(attr_elmt)) {
      attr = PyList_New(2);
//      SET_VECTOR_ELT(attrs,j, allocVector( STRSXP,2));
//      attr = VECTOR_ELT(attrs,j);
      PyList_SetItem(attr, 0, PyUnicode_FromString(((Attr *)attr_elmt->data)->key));
      PyList_SetItem(attr, 1, PyUnicode_FromString(((Attr *)attr_elmt->data)->value));
//      SET_STRING_ELT(attr, 0, mkChar( ((Attr *)attr_elmt->data)->key ));
//      SET_STRING_ELT(attr, 1, mkChar( ((Attr *)attr_elmt->data)->value ));
      PyList_SetItem(attrs, j, attr);
      j++;
    }
    PyList_SetItem(node_attrs, i, attrs);
    i++;
  }

  edges = malloc(sizeof(List));
  list_init(edges, free);
  for (vertex_elmt = list_head(graph.vertices); vertex_elmt != NULL; vertex_elmt = list_next(vertex_elmt)) {
    vertex = (Vertex *)list_data(vertex_elmt);
    for (edge_elmt = list_head((List *)vertex->adjlist); edge_elmt != NULL; edge_elmt = list_next(edge_elmt)) {
      edge = (Edge *) list_data(edge_elmt);
      list_ins_next(edges, list_tail(edges), (void *) edge);
    }
  }

//  PROTECT(edgemat = allocVector(STRSXP,2*list_size(edges))); 
//  PROTECT(edge_attrs = allocVector(VECSXP,list_size(edges)));
  edgemat = PyList_New(list_size(edges));
  edge_attrs = PyList_New(list_size(edges));

  i=0;
  for (edge_elmt = list_head(edges); edge_elmt != NULL; edge_elmt = list_next(edge_elmt)) {
    edge = (Edge *) list_data(edge_elmt);
//    PyList_SetItem(edgemat, i, Py_BuildValue('ss',PyUnicode_FromString( ((Vertex *)edge->fromvertex)->id ));
//    PyList_SetItem(edgemat, i, Py_BuildValue("ss", PyUnicode_FromString( ((Vertex *)edge->fromvertex)->id ), PyUnicode_FromString( ((Vertex *)edge->tovertex)->id ) ));
    PyList_SetItem(edgemat, i, Py_BuildValue("ss", ((Vertex *)edge->fromvertex)->id , ((Vertex *)edge->tovertex)->id  ));
//    PyList_SetItem(edgemat, 2*i+1, PyUnicode_FromString( ((Vertex *)edge->tovertex)->id ));
//    SET_STRING_ELT(edgemat, 2*i, mkChar( ((Vertex *)edge->fromvertex)->id ));
//    SET_STRING_ELT(edgemat, 2*i+1, mkChar( ((Vertex *)edge->tovertex)->id ));

    attrs = PyList_New( list_size((List *)(edge->data)) );
//    SET_VECTOR_ELT(edge_attrs,i, allocVector( VECSXP,list_size((List *)(edge->data)) ));
//    attrs = VECTOR_ELT(edge_attrs,i);
    j=0;
    for (attr_elmt = list_head((List *)(edge->data)); attr_elmt != NULL; attr_elmt = list_next(attr_elmt)) {
      attr = PyList_New(2);
//      SET_VECTOR_ELT(attrs,j, allocVector( STRSXP,2));
//      attr = VECTOR_ELT(attrs,j);
      PyList_SetItem(attr, 0, PyUnicode_FromString( ((Attr *)attr_elmt->data)->key ));
      PyList_SetItem(attr, 1, PyUnicode_FromString( ((Attr *)attr_elmt->data)->value ));
//      SET_STRING_ELT(attr, 0, mkChar( ((Attr *)attr_elmt->data)->key ));
//      SET_STRING_ELT(attr, 1, mkChar( ((Attr *)attr_elmt->data)->value ));
      PyList_SetItem(attrs, j, attr);
      j++;
    }
    PyList_SetItem(edge_attrs, i, attrs);
    i++;
  }
/*
  PROTECT(dim = allocVector(INTSXP, 2));
  INTEGER(dim)[0] = 2;
  INTEGER(dim)[1] = list_size(edges);
  setAttrib(edgemat, R_DimSymbol, dim);

  SET_VECTOR_ELT(graphdata,0,nodes);
  SET_VECTOR_ELT(graphdata,1,node_attrs);
  SET_VECTOR_ELT(graphdata,2,edgemat);
  SET_VECTOR_ELT(graphdata,3,edge_attrs);
  SET_VECTOR_ELT(graphdata,4,preprocessor_lines);
  UNPROTECT(7);
*/
  graph_destroy(&graph);
  fclose(fh);
  PyList_SetItem(graphdata,0,nodes);
  PyList_SetItem(graphdata,1,node_attrs);
  PyList_SetItem(graphdata,2,edgemat);
  PyList_SetItem(graphdata,3,edge_attrs);
  PyList_SetItem(graphdata,4,preprocessor_lines);
  return(graphdata);
}

struct module_state {
    PyObject *error;
};

#if PY_MAJOR_VERSION >= 3
#define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))
#else
#define GETSTATE(m) (&_state)
static struct module_state _state;
#endif

static PyObject *
error_out(PyObject *m) {
    struct module_state *st = GETSTATE(m);
    PyErr_SetString(st->error, "something bad happened");
    return NULL;
}

static PyMethodDef pydotreader_methods[] =
{
     {"readdot", readdot, METH_VARARGS, "Read a DOT file."},
     {NULL, NULL, 0, NULL}
};
 
#if PY_MAJOR_VERSION >= 3

static int pydotreader_traverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int pydotreader_clear(PyObject *m) {
    Py_CLEAR(GETSTATE(m)->error);
    return 0;
}
static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "_pydotreader",
        NULL,
        sizeof(struct module_state),
        pydotreader_methods,
        NULL,
        pydotreader_traverse,
        pydotreader_clear,
        NULL
};
#define INITERROR return NULL
PyObject *
PyInit__pydotreader(void)

#else
#define INITERROR return


void
initpydotreader(void)
#endif
{
#if PY_MAJOR_VERSION >= 3
    PyObject *module = PyModule_Create(&moduledef);
#else
    PyObject *module = Py_InitModule("pydotreader", pydotreader_methods);
#endif

    if (module == NULL)
        INITERROR;
    struct module_state *st = GETSTATE(module);

    st->error = PyErr_NewException("pydotreader.Error", NULL, NULL);
    if (st->error == NULL) {
        Py_DECREF(module);
        INITERROR;
    }

#if PY_MAJOR_VERSION >= 3
    return module;
#endif
}
