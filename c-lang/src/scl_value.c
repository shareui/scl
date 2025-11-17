#include "scl_parser.h"
#include <stdlib.h>
#include <string.h>

/* alloc/realloc/strdup wrappers */
static void *xrealloc(void *p, size_t n) { return realloc(p, n); }
static void *xmalloc(size_t n) { return malloc(n); }
static char *xstrdup(const char *s) {
	size_t n = strlen(s);
	char *p = (char*)xmalloc(n + 1);
	if (!p) return NULL;
	memcpy(p, s, n + 1);
	return p;
}

/* make values */
scl_value_t *scl_make_null(void) {
	scl_value_t *v = (scl_value_t*)xmalloc(sizeof(*v));
	if (!v) return NULL;
	v->type = SCL_NULL;
	return v;
}

scl_value_t *scl_make_bool(bool b) { scl_value_t *v = scl_make_null(); if (!v) return NULL; v->type = SCL_BOOL; v->as.b = b; return v; }
scl_value_t *scl_make_num(long long i) { scl_value_t *v = scl_make_null(); if (!v) return NULL; v->type = SCL_NUM; v->as.i = i; return v; }
scl_value_t *scl_make_fl(double f) { scl_value_t *v = scl_make_null(); if (!v) return NULL; v->type = SCL_FL; v->as.f = f; return v; }
scl_value_t *scl_make_str(const char *s) { scl_value_t *v = scl_make_null(); if (!v) return NULL; v->type = SCL_STR; v->as.s = xstrdup(s ? s : ""); return v; }
scl_value_t *scl_make_ml(const char *s) { scl_value_t *v = scl_make_null(); if (!v) return NULL; v->type = SCL_ML; v->as.s = xstrdup(s ? s : ""); return v; }
scl_value_t *scl_make_class(void) { scl_value_t *v = scl_make_null(); if (!v) return NULL; v->type = SCL_CLASS; v->as.obj.items = NULL; v->as.obj.len = v->as.obj.cap = 0; return v; }
scl_value_t *scl_make_list(scl_type_t elem_type) { scl_value_t *v = scl_make_null(); if (!v) return NULL; v->type = SCL_LIST; v->as.list.items = NULL; v->as.list.len = v->as.list.cap = 0; v->as.list.element_type = elem_type; return v; }

/* put key/value into class */
int scl_class_put(scl_value_t *obj, const char *key, scl_value_t *val) {
	if (!obj || obj->type != SCL_CLASS) return -1;
	if (obj->as.obj.len == obj->as.obj.cap) {
		size_t ncap = obj->as.obj.cap ? obj->as.obj.cap * 2 : 8;
		void *p = xrealloc(obj->as.obj.items, ncap * sizeof(scl_entry_t));
		if (!p) return -1;
		obj->as.obj.items = (scl_entry_t*)p;
		obj->as.obj.cap = ncap;
	}
	obj->as.obj.items[obj->as.obj.len].key = xstrdup(key);
	obj->as.obj.items[obj->as.obj.len].value = val;
	obj->as.obj.len += 1;
	return 0;
}

/* push value into list */
int scl_list_push(scl_value_t *list, scl_value_t *val) {
	if (!list || list->type != SCL_LIST) return -1;
	if (!(val->type == SCL_BOOL || val->type == SCL_NUM || val->type == SCL_FL || val->type == SCL_STR || val->type == SCL_ML)) return -1;
	if (list->as.list.element_type == SCL_NULL) list->as.list.element_type = val->type == SCL_STR || val->type == SCL_ML ? SCL_STR : val->type;
	if ((val->type == SCL_ML) && list->as.list.element_type == SCL_STR) {}
	else if (val->type != list->as.list.element_type && !(list->as.list.element_type == SCL_FL && val->type == SCL_NUM)) return -1;
	if (list->as.list.len == list->as.list.cap) {
		size_t ncap = list->as.list.cap ? list->as.list.cap * 2 : 8;
		void *p = xrealloc(list->as.list.items, ncap * sizeof(scl_value_t));
		if (!p) return -1;
		list->as.list.items = (scl_value_t*)p;
		list->as.list.cap = ncap;
	}
	list->as.list.items[list->as.list.len++] = *val;
	free(val);
	return 0;
}

/* free helpers */
static void free_obj(scl_obj_t *o) { for (size_t i = 0; i < o->len; ++i) { free(o->items[i].key); scl_free(o->items[i].value); } free(o->items); }
static void free_list(scl_list_t *l) { for (size_t i = 0; i < l->len; ++i) scl_free(&l->items[i]); free(l->items); }

/* free value */
void scl_free(scl_value_t *v) {
	if (!v) return;
	switch (v->type) {
		case SCL_STR: case SCL_ML: free(v->as.s); break;
		case SCL_CLASS: free_obj(&v->as.obj); break;
		case SCL_LIST: free_list(&v->as.list); break;
		default: break;
	}
	free(v);
}

/* free error string */
void scl_free_error(char *err) { free(err); }