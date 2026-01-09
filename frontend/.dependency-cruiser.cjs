/** @type {import('dependency-cruiser').IConfiguration} */
module.exports = {
  forbidden: [
    {
      name: 'no-circular',
      severity: 'error',
      comment:
        'Circular dependencies create tight coupling and make code harder to maintain',
      from: {},
      to: {
        circular: true,
      },
    },
    {
      name: 'components-no-pages',
      severity: 'error',
      comment: 'Components should not import from pages - violates dependency flow',
      from: { path: '^src/components' },
      to: { path: '^src/pages' },
    },
    {
      name: 'utils-no-components',
      severity: 'warn',
      comment: 'Utils should be generic and not depend on components',
      from: { path: '^src/utils' },
      to: { path: '^src/components' },
    },
    {
      name: 'contexts-no-components',
      severity: 'warn',
      comment: 'Contexts should not depend on specific components',
      from: { path: '^src/contexts' },
      to: { path: '^src/components' },
    },
  ],
  options: {
    /* Which modules not to follow */
    doNotFollow: {
      path: 'node_modules',
    },
    /* Understand TypeScript */
    tsPreCompilationDeps: true,
    tsConfig: {
      fileName: './tsconfig.json',
    },
    /* Enhance with TypeScript type info */
    enhancedResolveOptions: {
      exportsFields: ['exports'],
      conditionNames: ['import', 'require', 'node', 'default'],
    },
    /* Report format */
    reporterOptions: {
      dot: {
        collapsePattern: 'node_modules/[^/]+',
      },
      archi: {
        collapsePattern: '^(node_modules|packages|src)/[^/]+',
      },
    },
  },
};
