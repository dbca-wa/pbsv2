import { createApp } from 'vue';
import { createPinia } from 'pinia';
import router from './router';
import App from './App.vue';
import helpers from '@/utils/helpers';
import { useUserStore } from '@/stores/user';
import { CkeditorPlugin } from '@ckeditor/ckeditor5-vue';
import govVue3Components from '@dbca/gov-vue3-components';
const jsZip = require('jszip');
// @ts-ignore
window.JSZip = jsZip;
import 'sweetalert2/dist/sweetalert2.css';
import '@dbca/gov-vue3-components/dist/assets/library-DJ5wR63R.css';
import '@/../node_modules/@fortawesome/fontawesome-free/css/all.min.css';

// Add CSRF Token to every request
const customHeaders = new Headers({
    'X-CSRFToken': helpers.getCookie('csrftoken'),
});
const customHeadersJSON = new Headers({
    'X-CSRFToken': helpers.getCookie('csrftoken'),
    'Content-Type': 'application/json',
});

const fetch = window.fetch;
window.fetch = ((originalFetch) => {
    return (...args) => {
        if (args.length > 1) {
            if (typeof args[1].body === 'string') {
                args[1].headers = customHeadersJSON;
            } else {
                args[1].headers = customHeaders;
            }
        }
        const result = originalFetch.apply(this, args);
        return result;
    };
})(fetch);

const pinia = createPinia();

const app = createApp(App);

app.config.globalProperties.$filters = {
    pretty(val, indent = 2) {
        if (typeof val !== 'object') {
            try {
                val = JSON.parse(val);
            } catch (err) {
                console.warn('value is not JSON');
                return val;
            }
        }
        return JSON.stringify(val, null, indent);
    },
};

app.use(router).use(govVue3Components).use(CkeditorPlugin).use(pinia);
router.isReady().then(() => app.mount('#app'));

const store = useUserStore();

// For every request at the moment in case groups / profile etc are updated
// TODO: Consider only updating when the user logs in or out
store.fetchUserData();
