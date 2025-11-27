#include "scl_parser.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

/* Use lexer internal interface */
#define SCL_LEX_INTERNAL
#include "scl_lexer.c"

typedef struct {
	token *toks;
	size_t pos, len;
	char *err;
} pstate;

static token *cur(pstate *ps) { return ps->pos < ps->len ? &ps->toks[ps->pos] : &ps->toks[ps->len-1]; }
static token *eat(pstate *ps, tok_type tp, const char *msg) {
	token *t = cur(ps);
	if (t->type != tp) { ps->err = strdup(msg); return NULL; }
	ps->pos++; return t;
}

static scl_value_t *parse_value_class(pstate *ps);
static scl_value_t *parse_parameter(pstate *ps);
static scl_value_t *parse_value_list(pstate *ps);
static scl_value_t *parse_value_dynamic(pstate *ps);

static scl_value_t *parse_bool_value(pstate *ps) {
	if (!eat(ps, T_LBRACE, "Expected '{'")) return NULL;
	token *t = cur(ps); if (t->type != T_BOOLEAN) { ps->err = strdup("Expected boolean"); return NULL; }
	bool b = t->b; ps->pos++;
	if (!eat(ps, T_RBRACE, "Expected '}'")) return NULL;
	return scl_make_bool(b);
}

static scl_value_t *parse_str_value(pstate *ps) {
	if (!eat(ps, T_LBRACE, "Expected '{'")) return NULL;
	token *t = cur(ps); if (t->type != T_STRING) { ps->err = strdup("Expected string"); return NULL; }
	char *s = t->s; t->s = NULL; ps->pos++;
	if (!eat(ps, T_RBRACE, "Expected '}'")) { free(s); return NULL; }
	scl_value_t *v = scl_make_str(s);
	free(s);
	return v;
}

static scl_value_t *parse_num_value(pstate *ps) {
	if (!eat(ps, T_LBRACE, "Expected '{'")) return NULL;
	token *t = cur(ps); if (t->type != T_NUMBER) { ps->err = strdup("Expected number"); return NULL; }
	long long i = t->i; ps->pos++;
	if (!eat(ps, T_RBRACE, "Expected '}'")) return NULL;
	return scl_make_num(i);
}

static scl_value_t *parse_fl_value(pstate *ps) {
	if (!eat(ps, T_LBRACE, "Expected '{'")) return NULL;
	token *t = cur(ps);
	double f;
	if (t->type == T_FLOAT) { f = t->f; ps->pos++; }
	else if (t->type == T_NUMBER) { f = (double)t->i; ps->pos++; }
	else { ps->err = strdup("Expected float or number"); return NULL; }
	if (!eat(ps, T_RBRACE, "Expected '}'")) return NULL;
	return scl_make_fl(f);
}

static scl_value_t *parse_ml_value(pstate *ps) {
	if (!eat(ps, T_LBRACE, "Expected '{'")) return NULL;
	token *t = cur(ps); if (t->type != T_MLSTRING) { ps->err = strdup("Expected multiline string"); return NULL; }
	char *s = t->s; t->s = NULL; ps->pos++;
	if (!eat(ps, T_RBRACE, "Expected '}'")) { free(s); return NULL; }
	scl_value_t *v = scl_make_ml(s);
	free(s);
	return v;
}

static scl_value_t *parse_value_class(pstate *ps) {
	if (!eat(ps, T_LBRACE, "Expected '{'")) return NULL;
	scl_value_t *obj = scl_make_class();
	while (cur(ps)->type != T_RBRACE) {
		pair_t pr = parse_parameter_pair(ps);
		if (ps->err) { if (pr.key) free(pr.key); if (pr.val) scl_free(pr.val); scl_free(obj); return NULL; }
		if (scl_class_put(obj, pr.key ? pr.key : "", pr.val) != 0) {
			if (pr.key) free(pr.key);
			if (pr.val) scl_free(pr.val);
			scl_free(obj);
			ps->err = strdup("class put failed");
			return NULL;
		}
		free(pr.key);
	}
	if (!eat(ps, T_RBRACE, "Expected '}'")) { scl_free(obj); return NULL; }
	return obj;
}

static scl_value_t *parse_value_list(pstate *ps) {
	if (!eat(ps, T_LPAREN, "Expected '('")) return NULL;
	token *et = cur(ps);
	scl_type_t etype = SCL_NULL;
	if (et->type == T_NUMKW) { etype = SCL_NUM; ps->pos++; }
	else if (et->type == T_FLKW) { etype = SCL_FL; ps->pos++; }
	else if (et->type == T_BOOLKW) { etype = SCL_BOOL; ps->pos++; }
	else if (et->type == T_STRKW) { etype = SCL_STR; ps->pos++; }
	else { ps->err = strdup("Unsupported list element type"); return NULL; }
	if (!eat(ps, T_RPAREN, "Expected ')'")) return NULL;
	if (!eat(ps, T_LBRACE, "Expected '{'")) return NULL;
	scl_value_t *list = scl_make_list(etype);
	while (cur(ps)->type != T_RBRACE) {
		scl_value_t *ev = NULL;
		if (etype == SCL_NUM && cur(ps)->type == T_NUMBER) { ev = scl_make_num(cur(ps)->i); ps->pos++; }
		else if (etype == SCL_FL && (cur(ps)->type == T_FLOAT || cur(ps)->type == T_NUMBER)) { ev = scl_make_fl(cur(ps)->type == T_FLOAT ? cur(ps)->f : (double)cur(ps)->i); ps->pos++; }
		else if (etype == SCL_BOOL && cur(ps)->type == T_BOOLEAN) { ev = scl_make_bool(cur(ps)->as.b); ps->pos++; }
		else if (etype == SCL_STR && (cur(ps)->type == T_STRING)) { char *s = cur(ps)->s; cur(ps)->s = NULL; ps->pos++; ev = scl_make_str(s); free(s); }
		else { ps->err = strdup("List element type mismatch"); scl_free(list); return NULL; }
		if (scl_list_push(list, ev) != 0) { scl_free(ev); scl_free(list); ps->err = strdup("List push failed"); return NULL; }
		if (cur(ps)->type == T_COMMA) { ps->pos++; }
		else if (cur(ps)->type != T_RBRACE) { scl_free(list); ps->err = strdup("Expected comma or closing brace"); return NULL; }
	}
	if (!eat(ps, T_RBRACE, "Expected '}'")) { scl_free(list); return NULL; }
	return list;
}

static scl_value_t *parse_value_dynamic(pstate *ps) {
	if (!eat(ps, T_LBRACE, "Expected '{'")) return NULL;
	scl_value_t *v = NULL;
	if (cur(ps)->type == T_NUMBER) { v = scl_make_num(cur(ps)->i); ps->pos++; }
	else if (cur(ps)->type == T_FLOAT) { v = scl_make_fl(cur(ps)->f); ps->pos++; }
	else if (cur(ps)->type == T_BOOLEAN) { v = scl_make_bool(cur(ps)->b); ps->pos++; }
	else if (cur(ps)->type == T_STRING) { char *s = cur(ps)->s; cur(ps)->s = NULL; ps->pos++; v = scl_make_str(s); free(s); }
	else if (cur(ps)->type == T_MLSTRING) { char *s = cur(ps)->s; cur(ps)->s = NULL; ps->pos++; v = scl_make_ml(s); free(s); }
	else { ps->err = strdup("dynamic supports only base types (bool, str, num, fl, ml)"); return NULL; }
	if (!eat(ps, T_RBRACE, "Expected '}'")) { scl_free(v); return NULL; }
	return v;
}

/* Parse root object */
static scl_value_t *parse_root(pstate *ps) {
	scl_value_t *root = scl_make_class();
	while (cur(ps)->type != T_EOF) {
		if (cur(ps)->type == T_NEWLINE || cur(ps)->type == T_COMMENT) { ps->pos++; continue; }
		pair_t pr = parse_parameter_pair(ps);
		if (ps->err) { if (pr.key) free(pr.key); if (pr.val) scl_free(pr.val); scl_free(root); return NULL; }
		if (scl_class_put(root, pr.key ? pr.key : "", pr.val) != 0) {
			if (pr.key) free(pr.key);
			if (pr.val) scl_free(pr.val);
			scl_free(root);
			ps->err = strdup("put failed");
			return NULL;
		}
		free(pr.key);
	}
	return root;
}

/* Parse string buffer */
int scl_loads(const char *text, scl_value_t **out_value, char **out_error) {
	if (!text || !out_value) return -1;
	char *err = NULL;
	scl_tokens_view tv = scl_tokens_from_text(text, &err);
	if (err) { if (out_error) *out_error = err; return -1; }
	pstate ps = {0}; ps.toks = tv.toks; ps.len = tv.len; ps.pos = 0; ps.err = NULL;
	scl_value_t *val = parse_root(&ps);
	for (size_t i = 0; i < tv.len; ++i) {
		if (tv.toks[i].s) free(tv.toks[i].s);
	}
	free(tv.toks);
	if (!val) {
		if (out_error) *out_error = ps.err ? ps.err : strdup("Parse error");
		return -1;
	}
	*out_value = val;
	return 0;
}

/* Load from file */
int scl_load_file(const char *path, scl_value_t **out_value, char **out_error) {
	FILE *f = fopen(path, "rb");
	if (!f) { if (out_error) *out_error = strdup("Open failed"); return -1; }
	fseek(f, 0, SEEK_END); long n = ftell(f); fseek(f, 0, SEEK_SET);
	char *buf = (char*)malloc((size_t)n + 1); if (!buf) { fclose(f); if (out_error) *out_error = strdup("OOM"); return -1; }
	if (fread(buf, 1, (size_t)n, f) != (size_t)n) { fclose(f); free(buf); if (out_error) *out_error = strdup("Read failed"); return -1; }
	fclose(f); buf[n] = 0;
	int rc = scl_loads(buf, out_value, out_error);
	free(buf);
	return rc;
}

/* String builder helpers */
static void sb_append(char **buf, size_t *len, size_t *cap, const char *s) {
	size_t m = strlen(s);
	if (*len + m + 1 > *cap) {
		size_t ncap = *cap ? *cap * 2 : 256;
		while (ncap < *len + m + 1) ncap *= 2;
		char *nb = (char*)realloc(*buf, ncap);
		if (!nb) return;
		*buf = nb; *cap = ncap;
	}
	memcpy(*buf + *len, s, m); *len += m; (*buf)[*len] = 0;
}

static void sb_appendf(char **buf, size_t *len, size_t *cap, const char *fmt, ...) {
	char tmp[256];
	va_list ap; va_start(ap, fmt);
	int n = vsnprintf(tmp, sizeof(tmp), fmt, ap);
	va_end(ap);
	if (n < 0) return;
	if (n < (int)sizeof(tmp)) { sb_append(buf, len, cap, tmp); return; }
	char *dyn = (char*)malloc((size_t)n + 1);
	va_start(ap, fmt); vsnprintf(dyn, (size_t)n + 1, fmt, ap); va_end(ap);
	sb_append(buf, len, cap, dyn);
	free(dyn);
}

/* Internal recursive serializer */
static void dumps_inner(const scl_value_t *v, int indent, int level, char **buf, size_t *len, size_t *cap);

static void indent_write(int indent, int level, char **buf, size_t *len, size_t *cap) {
	for (int i = 0; i < indent * level; ++i) sb_append(buf, len, cap, " ");
}

/* Serialize one key/value line */
static void dumps_value_line(const char *key, const scl_value_t *v, int indent, int level, char **buf, size_t *len, size_t *cap) { ... }

/* Serialize class recursively */
static void dumps_inner(const scl_value_t *v, int indent, int level, char **buf, size_t *len, size_t *cap) {
	if (v->type == SCL_CLASS) {
		for (size_t i = 0; i < v->as.obj.len; ++i) {
			dumps_value_line(v->as.obj.items[i].key, v->as.obj.items[i].value, indent, level, buf, len, cap);
			if (i + 1 < v->as.obj.len) sb_append(buf, len, cap, "\n");
		}
	}
}

/* Dump to string */
char *scl_dumps(const scl_value_t *value, int indent, char **out_error) {
	char *buf = NULL; size_t len = 0, cap = 0;
	if (value->type == SCL_CLASS) {
		dumps_inner(value, indent <= 0 ? 4 : indent, 0, &buf, &len, &cap);
		sb_append(&buf, &len, &cap, "\n");
	} else {
		dumps_value_line("root", value, indent <= 0 ? 4 : indent, 0, &buf, &len, &cap);
		sb_append(&buf, &len, &cap, "\n");
	}
	return buf ? buf : strdup("");
}

/* Dump to file */
int scl_dump_file(const scl_value_t *value, const char *path, int indent, char **out_error) {
	char *s = scl_dumps(value, indent, out_error);
	FILE *f = fopen(path, "wb");
	if (!f) { if (out_error) *out_error = strdup("Open failed"); free(s); return -1; }
	fwrite(s, 1, strlen(s), f);
	fclose(f);
	free(s);
	return 0;
}