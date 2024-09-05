import { createRouter, createWebHistory } from 'vue-router';
import { RouterView } from 'vue-router';
import AccountsHome from '@/components/accounts/AccountsHome.vue';
import ComponentSearch from '@/components/search/ComponentSearch.vue';
import ProfileComponent from '@/components/accounts/Profile.vue';
import BurnPlanning from '@/components/burn-planning/BurnPlanning.vue';
import BurnPlanElement from '@/components/burn-planning/BurnPlanElement.vue';
import BurnPlanningUnits from '@/components/burn-planning/BurnPlanningUnits.vue';
import BurnPlanUnit from '@/components/burn-planning/BurnPlanUnit.vue';
import OperationalPlanning from '@/components/operational-planning/OperationalPlanning.vue';
import OperationalPlan from '@/components/operational-planning/OperationalPlan.vue';

const NotFoundComponent = null;
const router = createRouter({
    history: createWebHistory(),
    strict: false,
    routes: [
        {
            path: '/',
            name: 'home',
            component: AccountsHome,
        },
        {
            path: '/search',
            name: 'search',
            component: ComponentSearch,
        },
        {
            path: '/:pathMatch(.+)',
            component: NotFoundComponent,
        },
        {
            path: '/profile/',
            name: 'profile',
            component: ProfileComponent,
        },
        {
            path: '/burn-planning',
            name: 'burn-planning',
            component: BurnPlanning,
        },
        {
            path: '/burn-plan-elements/:pk',
            name: 'burn-plan-elements',
            component: BurnPlanElement,
        },
        {
            path: '/burn-planning-units',
            name: 'burn-planning-units',
            component: RouterView,
            children: [
                {
                    path: '',
                    name: 'burn-planning-units-list',
                    component: BurnPlanningUnits,
                },
                {
                    path: ':pk',
                    name: 'burn-planning-unit',
                    component: BurnPlanUnit,
                },
            ],
        },
        {
            path: '/operational-planning',
            name: 'operational-planning',
            component: OperationalPlanning,
        },
        {
            path: '/operational-plan/:pk',
            name: 'operational-plan',
            component: OperationalPlan,
        },
    ],
});

export default router;
