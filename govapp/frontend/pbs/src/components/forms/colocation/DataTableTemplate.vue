<template>
    <BootstrapAccordion
        v-if="withFilters"
        :id="datatableRefName + '-filters'"
        class="px-2 pt-2 pb-4"
    >
        <BootstrapAccordionItem heading="Filters">
            <SelectFilterTemplate
                :columns="columns"
                @selection-changed-select="
                    $emit('selection-changed-select', $event)
                "
                @selection-changed-remove="
                    $emit('selection-changed-remove', $event)
                "
            ></SelectFilterTemplate>
        </BootstrapAccordionItem>
    </BootstrapAccordion>

    <DataTable
        :ref="datatableRefName"
        v-bind="$attrs"
        :columns="tableColumns"
        :ajax="ajax"
        :options="options"
        class="text-capitalize"
        :class="tableClass"
        @vue:mounted="() => $emit('mounted')"
    >
    </DataTable>
</template>

<script>
import _ from 'lodash';
import { helpers } from '@/utils/hooks';

import SelectFilterTemplate from '@/components/forms/colocation/SelectFilterTemplate.vue';

import BootstrapAccordion from '@/components/forms/BootstrapAccordion.vue';
import BootstrapAccordionItem from '@/components/forms/BootstrapAccordionItem.vue';

import DataTable from 'datatables.net-vue3';
import DataTablesCore from 'datatables.net-bs5';
import Select from 'datatables.net-select-bs5';
import Buttons from 'datatables.net-buttons-bs5';
import Responsive from 'datatables.net-responsive-bs5';

DataTable.use(DataTablesCore);
DataTable.use(Select);
DataTable.use(Buttons);
DataTable.use(Responsive);

export default {
    name: 'DataTableTemplate',
    components: {
        BootstrapAccordion,
        BootstrapAccordionItem,
        DataTable,
        SelectFilterTemplate,
    },
    props: {
        /**
         * Name of the table
         */
        name: {
            type: String,
            required: true,
        },
        /**
         * The ajax endpoint string or object to fetch data from
         */
        ajax: {
            type: [String, Object],
            required: true,
        },
        /**
         * A list of dictionaries in the form of [{data: 'column', title: 'Column Title'}, ...]
         * Use either this or headers. Columns take precedence over headers
         * Example:
         * [
         *      {
                    data: 'data_field',
                    title: 'Data Field',
                    filter: false, // Adds a dropdown filter. optional, default is false
                    filterOptions: ['option1', 'option2', ...],
                },
                ...
            ]
         */
        columns: {
            type: Array,
            required: false,
            default: () => [],
        },
        /**
         * Options for the DataTable component
         */
        options: {
            type: Object,
            required: false,
            default: () => ({
                responsive: true,
                select: false,
                dom: '<"container-fluid"<"row"<"col"l><"col"f><"col"<"float-end"B>>>>rtip', // 'lfBrtip'
                buttons: ['copy', 'csv', 'excel'],
            }),
        },
        /**
         * A string of classes to apply to the table
         */
        tableClass: {
            type: String,
            required: false,
            default: 'table table-hover table-striped',
        },
        /**
         * A list of headers that correspond to column names in the queryset
         * Use either this or columns. Columns take precedence over headers
         */
        headers: {
            type: Array,
            required: false,
            default: () => [],
        },
        withFilters: {
            type: Boolean,
            required: false,
            default: false,
        },
    },
    emits: ['selection-changed-select', 'selection-changed-remove', 'mounted'],
    computed: {
        datatableRefName: function () {
            return this.name + 'Datatable';
        },
        /**
         * Columns object for the DataTable component
         */
        tableColumns: function () {
            // If columns are provided, use them
            if (this.columns.length) {
                return this.columns;
            }
            // Otherwise, derive from headers headers
            const columns = [];
            _.forEach(this.headers, (value) => {
                columns.push({
                    data: value,
                    title: this.replaceUnderscores(value),
                });
            });
            if (columns.length) {
                return columns;
            }
            // If no headers are provided, use id as the default
            return [{ data: 'id', title: 'Id' }];
        },
    },
    watch: {
        ajax: {
            // eslint-disable-next-line no-unused-vars
            handler: function (val) {
                // Reload the table when the ajax prop changes
                this.$refs[this.datatableRefName].dt.ajax.reload();
            },
        },
    },
    methods: {
        replaceUnderscores: helpers.replaceUnderscores,
        /**
         * Converts a queryset and headers to a format that DataTables can understand
         * @param {Array} queryset
         * @param {Array} headers A list of column headers
         * @returns {Array} A list of rows, each row is an array of values
         */
        tableData: function (queryset, headers) {
            const table_data = _.reduce(
                queryset,
                (result, value /**, key*/) => {
                    // Initialize the table row with null values
                    const row_full = {};
                    _.forEach(headers, (v /**, k*/) => {
                        row_full[v] = null;
                    });
                    // Pick queryset row values by headers
                    const row_serialized = _.pickBy(value, (v, k) => {
                        return headers.includes(k);
                    });
                    // Merge the two rows, overwriting null values where applicable
                    const row_merged = { ...row_full, ...row_serialized };
                    // Sort by headers order, create an array, and push to result
                    const row = _.zip(
                        ..._.chain(row_merged).toPairs().sortBy(headers).value()
                    )[1];
                    result.push(row);
                    return result;
                },
                []
            );

            return table_data;
        },
    },
};
</script>

<style scoped>
@import 'datatables.net-bs5';
@import 'datatables.net-responsive-bs5';
</style>
