<template lang="html">
    <div :class="headerCSS">
        <ul v-if="numDocuments > 0" class="list-group mb-3">
            <li v-for="v in documents" :key="v.id" class="list-group-item">
                <div>
                    <span v-if="v.name.endsWith('.pdf')" class="fa fa-file-pdf">
                        &nbsp;
                    </span>
                    <span v-else class="fa fa-file"> &nbsp; </span>
                    <a
                        :href="
                            Object.hasOwn(v, 'secure_url')
                                ? v.secure_url
                                : v.file
                        "
                        target="_blank"
                    >
                        {{ v.name }}
                    </a>
                    <span v-if="!readonly">
                        &nbsp;<a
                            class="bi bi-trash3"
                            title="Remove file"
                            :filename="v.name"
                            style="cursor: pointer; color: red"
                            @click="delete_document(v)"
                        ></a>
                    </span>
                </div>
            </li>
        </ul>
        <div v-if="show_spinner">
            <BootstrapSpinner
                class="text-primary"
                :center-of-screen="false"
                :small="true"
            />
        </div>
        <div
            v-if="
                (isRepeatable || (!isRepeatable && numDocuments === 0)) &&
                !show_spinner &&
                !readonly
            "
        >
            <input
                :id="name"
                :key="name"
                :name="name"
                type="file"
                :accept="fileTypes"
                class=""
                :class="ffu_input_element_classname"
                @change="handleChangeWrapper"
            />
            <div v-if="replaceButtonByText">
                <span
                    :id="'button-' + name"
                    class="btn btn-primary ffu-input-text"
                    @click="button_clicked(name)"
                >
                    <i class="fa fa-upload" aria-hidden="true"></i>&nbsp;
                    {{ textString }}</span
                >
            </div>
        </div>
    </div>
</template>

<script>
import { apiEndpoints, helpers } from '@/utils/hooks';
import Swal from 'sweetalert2';

export default {
    name: 'FileField',
    props: {
        headerCSS: {
            type: String,
            default: '',
        },
        name: {
            type: String,
            default: '',
        },
        label: {
            type: String,
            default: '',
        },
        id: {
            type: String,
            default: '',
        },
        fileTypes: {
            type: String,
            default: function () {
                const file_types =
                    'image/*,' +
                    'video/*,' +
                    'audio/*,' +
                    'application/pdf,text/csv,application/msword,application/vnd.ms-excel,application/x-msaccess,' +
                    'application/x-7z-compressed,application/x-bzip,application/x-bzip2,application/zip,' +
                    '.dbf,.gdb,.gpx,.prj,.shp,.shx,' +
                    '.json,.kml,.gpx';
                return file_types;
            },
        },
        isRepeatable: {
            type: Boolean,
            default: false,
        },
        readonly: {
            type: Boolean,
            default: false,
        },
        documentActionUrl: {
            type: String,
            required: true,
        },
        temporaryDocumentCollectionId: {
            type: Number,
            default: 0,
        },

        // For optional text button
        replaceButtonByText: {
            type: Boolean,
            default: false,
        },
        textString: {
            type: String,
            default: 'Attach Document',
        },
        approvalType: {
            type: Number,
            required: true,
        },
        approvalTypeDocumentType: {
            type: Number,
            required: true,
        },
    },
    emits: ['update-parent', 'update-temp-doc-coll-id'],
    data: function () {
        return {
            show_spinner: false,
            documents: [],
            filename: null,
            help_text_url: '',
            commsLogId: null,
            temporary_document_collection_id: null,
        };
    },
    computed: {
        numDocuments: function () {
            if (this.documents) {
                return this.documents.length;
            } else {
                return 0;
            }
        },
        ffu_input_element_classname: function () {
            if (this.replaceButtonByText) {
                return 'ffu-input-elem';
            }
            return '';
        },
        csrf_token: function () {
            return helpers.getCookie('csrftoken');
        },
        document_action_url: function () {
            let url = '';
            if (this.documentActionUrl == 'temporary_document') {
                if (!this.temporary_document_collection_id) {
                    url = apiEndpoints.temporary_document();
                } else {
                    url =
                        apiEndpoints.temporary_document() +
                        this.temporary_document_collection_id +
                        '/process_temp_document/';
                }
            } else {
                url = this.documentActionUrl;
            }
            return url;
        },
    },
    watch: {
        documents: {
            handler: async function () {
                this.$emit('update-parent');
            },
            deep: true,
        },
        temporaryDocumentCollectionId: function () {
            // read in prop value
            if (this.temporaryDocumentCollectionId) {
                this.temporary_document_collection_id =
                    this.temporaryDocumentCollectionId;
                this.get_documents();
            }
        },
    },
    mounted: async function () {
        await this.$nextTick().then(async () => {
            if (
                this.documentActionUrl === 'temporary_document' &&
                !this.temporary_document_collection_id
            ) {
                // pass
            } else {
                await this.get_documents();
            }
        });
    },
    methods: {
        button_clicked: function (/** @type {any} */ value) {
            if (this.replaceButtonByText) {
                // Input field id contains the document name which may contain
                // special characters (e.g. !"#$%&'()*+,./:;<=>?@[]^`{|}~)
                // Exact match treats values as strings.
                $(`input[id='${value}']`).trigger('click');
            }
        },
        handleChange: async function (
            /** @type {{ target: { files: string | any[]; }; }} */ e
        ) {
            console.log('Change', e.target.files);
            if (e.target.files.length > 0) {
                await this.save_document(e);
            }
        },
        get_documents: async function () {
            const formData = new FormData();
            this.show_spinner = true;

            if (this.document_action_url) {
                formData.append('action', 'list');
                if (this.commsLogId) {
                    formData.append('comms_log_id', this.commsLogId);
                }
                formData.append('input_name', this.name);
                formData.append('csrfmiddlewaretoken', this.csrf_token);
                const res = await fetch(this.document_action_url, {
                    body: formData,
                    method: 'POST',
                });
                const resData = await res.json();
                this.documents = resData.filedata;
                this.commsLogId = resData.comms_instance_id;
            }
            this.show_spinner = false;
        },
        delete_all_documents: function () {
            console.log('aho');
            for (const item of this.documents) {
                this.delete_document(item);
            }
        },
        delete_document: async function (
            /** @type {{ id: string | Blob; }} */ file
        ) {
            const formData = new FormData();
            this.show_spinner = true;

            formData.append('action', 'delete');
            formData.append('input_name', this.name);
            if (this.commsLogId) {
                formData.append('comms_log_id', this.commsLogId);
            }
            formData.append('document_id', file.id);
            formData.append('csrfmiddlewaretoken', this.csrf_token);
            if (this.document_action_url) {
                const res = await fetch(this.document_action_url, {
                    body: formData,
                    method: 'POST',
                });
                const resData = await res.json();
                this.documents = resData.filedata;
                this.commsLogId = resData.comms_instance_id;
            }
            this.show_spinner = false;
        },
        cancel: async function () {
            this.show_spinner = true;

            const formData = new FormData();
            formData.append('action', 'cancel');
            formData.append('input_name', this.name);
            if (this.commsLogId) {
                formData.append('comms_log_id', this.commsLogId);
            }
            formData.append('csrfmiddlewaretoken', this.csrf_token);
            if (this.document_action_url) {
                await fetch(this.document_action_url, {
                    body: formData,
                    method: 'POST',
                });
            }
            this.show_spinner = false;
        },
        /**
         * @param {{ target: { files: any[]; }; }} e
         */
        uploadFile(e) {
            let _file = null;

            if (e.target.files && e.target.files[0]) {
                const reader = new FileReader();
                reader.readAsDataURL(e.target.files[0]);
                reader.onload = function (e) {
                    _file = e.target.result;
                };
                _file = e.target.files[0];
            }
            return _file;
        },
        /**
         * A handler
         * @param {any} e
         */
        handleChangeWrapper: async function (e) {
            this.show_spinner = true;
            if (
                this.documentActionUrl === 'temporary_document' &&
                !this.temporary_document_collection_id
            ) {
                // If temporary_document, create TemporaryDocumentCollection object and allow document_action_url to update
                const res = await fetch(this.document_action_url, {
                    method: 'POST',
                });
                const resData = await res.json();
                this.temporary_document_collection_id = resData.id;
                await this.handleChange(e);
                this.$emit(
                    'update-temp-doc-coll-id',
                    this.temporary_document_collection_id
                );
            } else {
                await this.handleChange(e);
            }
            this.show_spinner = false;
        },
        /**
         * Save document to database
         * @param {any} e
         */
        save_document: async function (e) {
            const formData = new FormData();
            if (this.document_action_url) {
                formData.append('action', 'save');
                if (this.commsLogId) {
                    formData.append('comms_log_id', this.commsLogId);
                }
                if (this.temporary_document_collection_id) {
                    formData.append(
                        'temporary_document_collection_id',
                        this.temporary_document_collection_id
                    );
                }
                formData.append('input_name', this.name);
                formData.append('approval_type', this.approvalType.toString());
                formData.append(
                    'approval_type_document_type',
                    this.approvalTypeDocumentType.toString()
                );
                formData.append('filename', e.target.files[0].name);
                formData.append('_file', this.uploadFile(e));
                formData.append('csrfmiddlewaretoken', this.csrf_token);

                await fetch(this.document_action_url, {
                    body: formData,
                    method: 'POST',
                })
                    .then(async (response) => {
                        if (!response.ok) {
                            return await response.json().then((json) => {
                                throw new Error(json);
                            });
                        } else {
                            return await response.json();
                        }
                    })
                    .then((data) => {
                        this.documents = data.filedata;
                        this.commsLogId = data.comms_instance_id;
                    })
                    .catch((error) => {
                        Swal.fire({
                            title: 'File Error',
                            text: error,
                            icon: 'error',
                        });
                    });
            }
        },
    },
};
</script>

<style scoped lang="css">
input {
    box-shadow: none;
}

.ffu-input-elem {
    display: none !important;
}
.ffu-input-text {
    color: #337ab7;
    cursor: pointer;
}

.list-group {
    display: inline-block;
}
</style>
