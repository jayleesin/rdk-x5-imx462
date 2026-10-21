// SPDX-License-Identifier: GPL-2.0-only
// Local ABI metadata checker; publication notice added 2026-10-21.
#include <stdio.h>
#include <stddef.h>
#include <dlfcn.h>
#include "hb_cam_utility.h"
int main(int argc,char **argv) {
    if(argc != 3) return 2;
    void *h=dlopen(argv[1],RTLD_NOW|RTLD_LOCAL);
    if(!h) { fprintf(stderr,"%s\n",dlerror()); return 1; }
    sensor_module_t *s=dlsym(h,argv[2]);
    if(!s || !CAMERA_MODULE_CHECK_VALID(s->module_st)) return 1;
    const camera_module_t *m=s->module_st;
    printf("%s module=%u/%zu info=%u/%zu data=%u version=%08x flags=%08x\n",
      m->name,m->module_size,sizeof(*s),m->info_size,sizeof(sensor_info_t),m->data_size,m->version,m->flags);
    int ok=m->module_size==sizeof(*s) && m->info_size==sizeof(sensor_info_t);
    dlclose(h); return ok?0:1;
}
