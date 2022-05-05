TAG 			:= latest	
USER 			:= eaholman
PROJECT			:= user_portal

IMG_WEB_SVC    			:= ${USER}/${PROJECT}:${TAG}
IMG_WEB_SVC_JYP    		:= ${USER}/${PROJECT_JYP}:${TAG}

ID_USER					:= ${shell id -u}
ID_GROUP				:= ${shell id -g}
.PHONY:

test:
		echo ${IMG_WEB_SVC}
		echo ${TAG}
		echo ${PROJECT}
		echo ${PROJECT}:${TAG}
		echo ${ID_USER}

build_docker:
	docker build -t ${IMG_WEB_SVC} ./docker

run_docker:
	docker run --rm --shm-size=1g --user="${ID_USER}:${ID_GROUP}" --ulimit memlock=-1 --ulimit stack=67108864 --memory-swap -1 -it -v ${PWD}:/work/ -v ${PWD}../../../data:/work/data/ -p 8052:8050 ${IMG_WEB_SVC} /bin/bash
	# why 8052:8050???

clean:
	find -name "*~" -delete
	-rm .python_history
	-rm -rf .config
	-rm -rf .cache
