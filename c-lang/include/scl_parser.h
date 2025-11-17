#ifndef SCL_PARSER_H
#define SCL_PARSER_H

#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
	SCL_BOOL,
	SCL_NUM,
	SCL_FL,
	SCL_STR,
	SCL_ML,
	SCL_CLASS,
	SCL_LIST,
	SCL_NULL
} scl_type_t;

typedef struct scl_value scl_value_t;

typedef struct {
	char *key;
	scl_value_t *value;
} scl_entry_t;

typedef struct {
	scl_entry_t *items;
	size_t len;
	size_t cap;
} scl_obj_t;

typedef struct {
	scl_value_t *items;
	size_t len;
	size_t cap;
	scl_type_t element_type;
} scl_list_t;

struct scl_value {
	scl_type_t type;
	union {
		bool b;
		long long i;
		double f;
		char *s;
		scl_obj_t obj;
		scl_list_t list;
	} as;
};

int scl_load_file(const char *path, scl_value_t **out_value, char **out_error);
int scl_loads(const char *text, scl_value_t **out_value, char **out_error);
int scl_dump_file(const scl_value_t *value, const char *path, int indent, char **out_error);
char *scl_dumps(const scl_value_t *value, int indent, char **out_error);

scl_value_t *scl_make_null(void);
scl_value_t *scl_make_bool(bool v);
scl_value_t *scl_make_num(long long v);
scl_value_t *scl_make_fl(double v);
scl_value_t *scl_make_str(const char *s);
scl_value_t *scl_make_ml(const char *s);
scl_value_t *scl_make_class(void);
scl_value_t *scl_make_list(scl_type_t elem_type);

int scl_class_put(scl_value_t *obj, const char *key, scl_value_t *val);
int scl_list_push(scl_value_t *list, scl_value_t *val);

void scl_free(scl_value_t *val);
void scl_free_error(char *err);

#ifdef __cplusplus
}
#endif

#endif