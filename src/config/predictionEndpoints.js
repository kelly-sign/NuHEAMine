// Public prediction API paths. Keeping these constants free of application
// dependencies allows both router metadata and API clients to import them
// without creating a router/request circular dependency.
export const predictionEndpoints = {
  hardness: '/api/v1/prediction/hardness',
  yieldStrength: '/api/v1/prediction/yield_strength',
  tensileStrength: '/api/v1/prediction/tensile_strength',
  phaseComposition: '/api/v1/prediction/phase',
  irradiationHardening: '/api/v1/prediction/irradiation_hardening',
  irradiationEmbrittlement: '/api/v1/prediction/irradiation_embrittlement'
}
