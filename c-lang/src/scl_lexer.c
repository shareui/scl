#include "scl_parser.h"
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

typedef enum {
	T_IDENT, T_DCOLON,
	T_BOOLKW, T_STRKW, T_NUMKW, T_FLKW, T_MLKW, T_CLASSKW, T_LISTKW, T_DYNAMICKW,
	T_LBRACE, T_RBRACE, T_LPAREN, T_RPAREN, T_COMMA,
	T_STRING, T_MLSTRING, T_NUMBER, T_FLOAT, T_BOOLEAN,
	T_COMMENT, T_NEWLINE, T_EOF
} tok_type;

typedef struct {
	tok_type type;
	char *s;
	double f;
	long long i;
	bool b;
	int line, col;
} token;

typedef struct {
	const char *text;
	size_t pos;
	int line, col;
	token *toks;
	size_t len, cap;
	char *err;
} lex_state;

/* push token */
static void push(lex_state *st, token tk) {
	if (st->len == st->cap) {
		size_t ncap = st->cap ? st->cap * 2 : 128;
		st->toks = (token*)realloc(st->toks, ncap * sizeof(token));
		st->cap = ncap;
	}
	st->toks[st->len++] = tk;
}

/* peek char */
static int peekc(lex_state *st, size_t off) {
	size_t i = st->pos + off;
	return st->text[i] ? (unsigned char)st->text[i] : -1;
}

/* next char */
static int adv(lex_state *st) {
	int c = peekc(st, 0);
	if (c < 0) return c;
	st->pos++;
	if (c == '\n') { st->line++; st->col = 1; } else { st->col++; }
	return c;
}

/* skip spaces/tabs */
static void skip_ws(lex_state *st) {
	int c = peekc(st, 0);
	while (c == ' ' || c == '\t') { adv(st); c = peekc(st, 0); }
}

/* copy substring */
static char *substr(const char *src, size_t a, size_t b) {
	size_t n = b - a;
	char *s = (char*)malloc(n + 1);
	memcpy(s, src + a, n);
	s[n] = 0;
	return s;
}

/* push simple token */
static void add_simple(lex_state *st, tok_type tp) {
	token tk = {0}; tk.type = tp; tk.line = st->line; tk.col = st->col; push(st, tk);
}

/* id char */
static int isident(int c) { return isalnum(c) || c == '_' || c == '-'; }

/* main lexer */
static int lex(lex_state *st) {
	while (1) {
		skip_ws(st);
		int c = peekc(st, 0);
		if (c < 0) break;

		/* comment */
		if (c == '[') {
			int line = st->line, col = st->col;
			adv(st);
			size_t start = st->pos;
			while (peekc(st, 0) >= 0 && peekc(st, 0) != ']') adv(st);
			if (peekc(st, 0) != ']') { st->err = strdup("Unclosed comment"); return -1; }
			char *s = substr(st->text, start, st->pos);
			adv(st);
			token tk = {0}; tk.type = T_COMMENT; tk.s = s; tk.line = line; tk.col = col; push(st, tk);
			continue;
		}

		/* newline */
		if (c == '\n') { add_simple(st, T_NEWLINE); adv(st); continue; }

		/* punctuation */
		if (c == ':' && peekc(st,1) == ':') { add_simple(st, T_DCOLON); adv(st); adv(st); continue; }
		if (c == '{') { add_simple(st, T_LBRACE); adv(st); continue; }
		if (c == '}') { add_simple(st, T_RBRACE); adv(st); continue; }
		if (c == '(') { add_simple(st, T_LPAREN); adv(st); continue; }
		if (c == ')') { add_simple(st, T_RPAREN); adv(st); continue; }
		if (c == ',') { add_simple(st, T_COMMA); adv(st); continue; }

		/* string */
		if (c == '"') {
			int line = st->line, col = st->col;
			adv(st);
			char *buf = (char*)malloc(1); buf[0] = 0; size_t blen = 0;
			while (peekc(st,0) >= 0 && peekc(st,0) != '"') {
				int ch = adv(st);
				if (ch == '\\') {
					int n = adv(st);
					char out = (n == 'n') ? '\n' : (n == 't') ? '\t' : (n == '"' || n == '\\') ? (char)n : (char)n;
					buf = (char*)realloc(buf, blen + 2); buf[blen++] = out; buf[blen] = 0;
				} else {
					buf = (char*)realloc(buf, blen + 2); buf[blen++] = (char)ch; buf[blen] = 0;
				}
			}
			if (peekc(st,0) != '"') { free(buf); st->err = strdup("Unclosed string"); return -1; }
			adv(st);
			token tk = {0}; tk.type = T_STRING; tk.s = buf; tk.line = line; tk.col = col; push(st, tk);
			continue;
		}

		/* multiline string */
		if (c == '\'') {
			int line = st->line, col = st->col;
			adv(st);
			size_t start = st->pos;
			while (peekc(st,0) >= 0 && peekc(st,0) != '\'') adv(st);
			if (peekc(st,0) != '\'') { st->err = strdup("Unclosed multiline string"); return -1; }
			char *s = substr(st->text, start, st->pos);
			adv(st);
			token tk = {0}; tk.type = T_MLSTRING; tk.s = s; tk.line = line; tk.col = col; push(st, tk);
			continue;
		}

		/* number or float (negative) */
		if (c == '-' && isdigit(peekc(st,1))) {
			int line = st->line, col = st->col;
			size_t start = st->pos;
			adv(st);
			int has_dot = 0;
			while (isdigit(peekc(st,0)) || peekc(st,0) == '.') { if (peekc(st,0)=='.'){ if(has_dot) break; has_dot=1;} adv(st); }
			char *s = substr(st->text, start, st->pos);
			token tk = {0}; tk.line=line; tk.col=col;
			if (strchr(s, '.')) { tk.type = T_FLOAT; tk.f = atof(s); }
			else { tk.type = T_NUMBER; tk.i = atoll(s); }
			free(s);
			push(st, tk);
			continue;
		}

		/* number or ident-like num */
		if (isdigit(c)) {
			int line = st->line, col = st->col;
			size_t p = st->pos;
			while (isdigit(peekc(st,0))) adv(st);
			if (isalpha(peekc(st,0)) || peekc(st,0) == '_') {
				while (isident(peekc(st,0))) adv(st);
				char *s = substr(st->text, p, st->pos);
				token tk = {0}; tk.type = T_IDENT; tk.s = s; tk.line=line; tk.col=col; push(st, tk);
			} else {
				char *s = substr(st->text, p, st->pos);
				token tk = {0}; tk.line=line; tk.col=col; tk.type = T_NUMBER; tk.i = atoll(s); free(s); push(st, tk);
			}
			continue;
		}

		/* identifier / keyword */
		if (isalpha(c) || c == '_') {
			int line = st->line, col = st->col;
			size_t start = st->pos;
			while (isident(peekc(st,0))) adv(st);
			char *s = substr(st->text, start, st->pos);
			tok_type tp = T_IDENT;
			if (!strcmp(s,"bool")) tp=T_BOOLKW;
			else if (!strcmp(s,"str")) tp=T_STRKW;
			else if (!strcmp(s,"num")) tp=T_NUMKW;
			else if (!strcmp(s,"fl")) tp=T_FLKW;
			else if (!strcmp(s,"ml")) tp=T_MLKW;
			else if (!strcmp(s,"class")) tp=T_CLASSKW;
			else if (!strcmp(s,"list")) tp=T_LISTKW;
			else if (!strcmp(s,"dynamic")) tp=T_DYNAMICKW;
			else if (!strcmp(s,"true")||!strcmp(s,"yes")) { tp=T_BOOLEAN; }
			else if (!strcmp(s,"false")||!strcmp(s,"no")) { tp=T_BOOLEAN; }
			if (tp == T_BOOLEAN) {
				bool b = (!strcmp(s,"true")||!strcmp(s,"yes"));
				free(s);
				token tk = {0}; tk.type=T_BOOLEAN; tk.b=b; tk.line=line; tk.col=col; push(st, tk);
			} else {
				token tk = {0}; tk.type=tp; tk.s=s; tk.line=line; tk.col=col; push(st, tk);
			}
			continue;
		}

		st->err = strdup("Unexpected char");
		return -1;
	}
	token eof = {0}; eof.type = T_EOF; eof.line = st->line; eof.col = st->col; push(st, eof);
	return 0;
}

/* expose lexer result */
#include <stdio.h>

typedef struct {
	token *items;
	size_t len;
	char *err;
} scl_lex_result;

static scl_lex_result scl_lex_all(const char *text) {
	lex_state st = {0};
	st.text = text; st.pos = 0; st.line = 1; st.col = 1;
	if (lex(&st) != 0) {
		for (size_t i = 0; i < st.len; ++i) {
			if (st.toks[i].s) free(st.toks[i].s);
		}
		scl_lex_result r = {0}; r.err = st.err ? st.err : strdup("Lex error"); return r;
	}
	scl_lex_result r = {0}; r.items = st.toks; r.len = st.len; r.err = NULL; return r;
}

/* simple token view */
#define SCL_LEX_INTERNAL
#ifdef SCL_LEX_INTERNAL
typedef struct {
	token *toks;
	size_t len;
} scl_tokens_view;

static scl_tokens_view scl_tokens_from_text(const char *text, char **out_err) {
	scl_lex_result r = scl_lex_all(text);
	if (r.err) { if (out_err) *out_err = r.err; return (scl_tokens_view){0}; }
	return (scl_tokens_view){ .toks = r.items, .len = r.len };
}
#endif